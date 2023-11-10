from datetime import datetime
from typing import List

import requests
from pydantic import BaseModel
from rich import print

headers = {"Cache-Control": "no-cache", "Content-Type": "application/json"}
endpoint = "latest_runs"


class DagRunItem(BaseModel):
    dag_id: str
    dag_run_url: str
    execution_date: datetime
    start_date: datetime


class LatestRunsResponse(BaseModel):
    items: List[DagRunItem]


# get the list of dags using the experimental airflow 1 api
r_dags = requests.get(
    "http://localhost:8082/api/experimental/latest_runs", headers=headers
)

# make pydantic model from the response
dags = LatestRunsResponse(**r_dags.json())

print(dags)


class DagPausedStatus(BaseModel):
    is_paused: bool
    dag_id: str


dags_with_status = []
# loop through dags and get the paused status of each dag
for dag in dags.items:
    r = requests.get(
        f"http://localhost:8082/api/experimental/dags/{dag.dag_id}/paused",
        headers=headers,
    )
    # make DagPausedStatus model from the response
    # and print the result
    o = DagPausedStatus(is_paused=r.json()["is_paused"], dag_id=dag.dag_id)
    print(o)
    dags_with_status.append(o)

# make a list of all the dags that are not paused
not_paused = [dag for dag in dags_with_status if not dag.is_paused]

# paused all not_paused dags
for dag in not_paused:
    r = requests.get(
        f"http://localhost:8082/api/experimental/dags/{dag.dag_id}/paused/true",
        headers=headers,
    )
    print(r.json())

input("enter to unapuse dags")

# unpaused the dags that were paused
for dag in not_paused:
    r = requests.get(
        f"http://localhost:8082/api/experimental/dags/{dag.dag_id}/paused/false",
        headers=headers,
    )
    print(r.json())
