import json
import logging
import platform
import time
from dataclasses import dataclass
from functools import wraps
from typing import List

import requests

# Setup logging with Rich
logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="[%X]")

headers = {"Cache-Control": "no-cache", "Content-Type": "application/json"}


# If the script is running on the host machine
if platform.system() == "Darwin":  # macOS
    AIRFLOW_URL = "http://localhost:8081"
else:
    AIRFLOW_URL = "http://host.docker.internal:8081"


@dataclass
class DagRunItem:
    dag_id: str
    dag_run_url: str
    execution_date: str
    start_date: str


@dataclass
class LatestRunsResponse:
    items: List[DagRunItem]


@dataclass
class DagPausedStatus:
    is_paused: bool
    dag_id: str


@dataclass
class PauseUnpauseResponse:
    dag_id: str
    response: str


def sleep_decorator(func):
    """
    Put measurable time in between API calls since it's experimental and I
    don't want to  hammer the API
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        time.sleep(0.1)
        return result

    return wrapper


@sleep_decorator
def get_dags() -> List[DagRunItem]:
    """Return a list of dags __that have been run on the airflow instance__

    NOTE: This is not a list of all dags in the system, just the ones that have run
    """
    logging.info("Fetching DAGs...")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/latest_runs", headers=headers
    )
    response.raise_for_status()
    return LatestRunsResponse(**response.json()).items


@sleep_decorator
def get_dag_status(dag_id) -> DagPausedStatus:
    """Return the paused status of a DAG

    Args:
        dag_id
    """
    logging.info(f"Fetching status for DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused", headers=headers
    )
    response.raise_for_status()
    logging.info(f"DAG Paused: {response.json()['is_paused']}")
    return DagPausedStatus(is_paused=response.json()["is_paused"], dag_id=dag_id)


@sleep_decorator
def get_non_paused_dags() -> List[DagPausedStatus]:
    dags = get_dags()

    dags_with_status = [get_dag_status(dag.get("dag_id")) for dag in dags]

    non_paused_dags = [dag for dag in dags_with_status if not dag.is_paused]

    return non_paused_dags


@sleep_decorator
def pause_dag(dag_id):
    """Set a DAG's paused status to True

    Args:
        dag_id
    """
    logging.info(f"Pausing DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused/true", headers=headers
    )
    response.raise_for_status()
    return PauseUnpauseResponse(**response.json(), dag_id=dag_id)


@sleep_decorator
def unpause_dag(dag_id):
    """Set a DAG's paused status to False

    Args:
        dag_id
    """
    logging.info(f"Unpausing DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused/false", headers=headers
    )
    response.raise_for_status()
    return PauseUnpauseResponse(**response.json(), dag_id=dag_id)


def main():
    # Get all non-paused DAGs
    non_paused_dags = get_non_paused_dags()

    # Pause all non-paused DAGs
    for dag in non_paused_dags:
        pause_dag(dag.dag_id)

    # Serialize the list of non-paused DAGs to JSON
    non_paused_dags_json = json.dumps([dag.__dict__ for dag in non_paused_dags])

    # Write the JSON to a file
    with open("dags.json", "w") as f:
        f.write(non_paused_dags_json)

    # TODO: should this be a seaprate cron job to unpause them?
    print("sleeping 10 seconds before unpausing the dags again")
    time.sleep(10)

    # Load the JSON from the file
    with open("dags.json", "r") as f:
        non_paused_dags = [DagPausedStatus(**dag) for dag in json.loads(f.read())]

    # Unpause the DAGs
    for dag in non_paused_dags:
        unpause_dag(dag.dag_id)


if __name__ == "__main__":
    unpause_dag("tutorial")
    main()
