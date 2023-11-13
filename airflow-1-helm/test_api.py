import logging
import time
from datetime import datetime
from functools import wraps
from typing import List

import requests
from pydantic import BaseModel
from rich.logging import RichHandler
from rich.prompt import Prompt

# Setup logging with Rich
logging.basicConfig(
    level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

headers = {"Cache-Control": "no-cache", "Content-Type": "application/json"}
AIRFLOW_URL = "http://localhost:8081"


class DagRunItem(BaseModel):
    dag_id: str
    dag_run_url: str
    execution_date: datetime
    start_date: datetime


class LatestRunsResponse(BaseModel):
    items: List[DagRunItem]


class DagPausedStatus(BaseModel):
    is_paused: bool
    dag_id: str


class PauseUnpauseResponse(BaseModel):
    dag_id: str
    response: str


def sleep_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        time.sleep(0.25)
        return result

    return wrapper


@sleep_decorator
def get_dags():
    logging.info("Fetching DAGs...")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/latest_runs", headers=headers
    )
    response.raise_for_status()
    return LatestRunsResponse(**response.json()).items


@sleep_decorator
def get_dag_status(dag_id):
    logging.info(f"Fetching status for DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused", headers=headers
    )
    response.raise_for_status()
    logging.info(f"DAG Paused: {response.json()['is_paused']}")
    return DagPausedStatus(is_paused=response.json()["is_paused"], dag_id=dag_id)


@sleep_decorator
def pause_dag(dag_id):
    logging.info(f"Pausing DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused/true", headers=headers
    )
    response.raise_for_status()
    return PauseUnpauseResponse(**response.json(), dag_id=dag_id)


@sleep_decorator
def unpause_dag(dag_id):
    logging.info(f"Unpausing DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused/false", headers=headers
    )
    response.raise_for_status()
    return PauseUnpauseResponse(**response.json(), dag_id=dag_id)


def main():
    dags = get_dags()
    dags_with_status = [get_dag_status(dag.dag_id) for dag in dags]
    not_paused = [dag for dag in dags_with_status if not dag.is_paused]

    for dag in not_paused:
        r = pause_dag(dag.dag_id)

        logging.info(r)

    Prompt.ask("Press enter to unpause dags")

    for dag in not_paused:
        r = unpause_dag(dag.dag_id)

        logging.info(r)


if __name__ == "__main__":
    unpause_dag("tutorial")
    main()
