import logging
from datetime import datetime
from typing import List

import requests
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

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


def get_dags():
    logging.info("Fetching DAGs...")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/latest_runs", headers=headers
    )
    response.raise_for_status()
    return LatestRunsResponse(**response.json()).items


def get_dag_status(dag_id):
    logging.info(f"Fetching status for DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused", headers=headers
    )
    response.raise_for_status()
    return DagPausedStatus(is_paused=response.json()["is_paused"], dag_id=dag_id)


def pause_dag(dag_id):
    logging.info(f"Pausing DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused/true", headers=headers
    )
    response.raise_for_status()
    return response.json()


def unpause_dag(dag_id):
    logging.info(f"Unpausing DAG: {dag_id}")
    response = requests.get(
        f"{AIRFLOW_URL}/api/experimental/dags/{dag_id}/paused/false", headers=headers
    )
    response.raise_for_status()
    return response.json()


def main():
    dags = get_dags()
    dags_with_status = [get_dag_status(dag.dag_id) for dag in dags]
    not_paused = [dag for dag in dags_with_status if not dag.is_paused]

    for dag in not_paused:
        pause_dag(dag.dag_id)

    input("Press enter to unpause dags")

    for dag in not_paused:
        unpause_dag(dag.dag_id)


if __name__ == "__main__":
    main()
