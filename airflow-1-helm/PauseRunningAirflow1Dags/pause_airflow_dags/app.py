import json
import logging
import os
import platform
import socket
import time
from datetime import datetime
from functools import wraps
from typing import List

import requests
from pydantic import BaseModel
from rich.logging import RichHandler

# Setup logging with Rich
logging.basicConfig(
    level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

headers = {"Cache-Control": "no-cache", "Content-Type": "application/json"}


def is_docker():
    # Check if the script is running inside a Docker container
    return os.getenv("HOSTNAME", "").startswith("docker-")


if is_docker():
    # If the script is running inside a Docker container
    AIRFLOW_URL = "http://host.docker.internal:8081"
else:
    # If the script is running on the host machine
    if platform.system() == "Darwin":  # macOS
        AIRFLOW_URL = "http://localhost:8081"
    else:  # Linux
        AIRFLOW_URL = f"http://{socket.gethostbyname(socket.gethostname())}:8081"


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
    dags = get_dags()
    dags_with_status = [get_dag_status(dag.dag_id) for dag in dags]
    not_paused = [dag for dag in dags_with_status if not dag.is_paused]

    for dag in not_paused:
        r = pause_dag(dag.dag_id)

        logging.info(r)

    # Prompt.ask("Press enter to unpause dags")
    print("sleeping 10 seconds before unpausing")
    time.sleep(10)

    for dag in not_paused:
        r = unpause_dag(dag.dag_id)

        logging.info(r)


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    unpause_dag("tutorial")
    main()

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Ran Pause/Unpause DAGs",
            }
        ),
    }


if __name__ == "__main__":
    if not is_docker():
        main()
