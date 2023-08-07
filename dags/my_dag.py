"hello world airflow dag"
import time
from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from airflow.configuration import ConfigParser

# TODO: Am I writing this for task or dag level hcio? I think DAG so the task
# level callback is not what I need to do... just a function that takes a slug
# to be tacked onto the end of a DAG in campaign

# I think this is all that really needs to be configured...
PROJECT_PING_KEY = "844d7hQguj_-hZ26ByMAeA"

# TODO: remove default slug value
def hcio_dag_alert(slug: str = 'data-80123', **kwargs):
    """Function to be used a python_callable for DAG Healthcheck with hcio

    Args:
        slug: slug id of hcio endpoint to use - endpoints are to be created in avant-data-gitops repo
        **kwargs: Airflow context
    """
    slug = kwargs.get('slug')
    success = kwargs.get('success', True)

    url =f"https://hc-ping.com/{PROJECT_PING_KEY}/{slug}"
    requests.get(url if success is True else url + "/fail")

def hcio_task_alert(ctxt: dict):
    """HCIO alert utility for drop-in hcio integration to Airflow tasks

    Args:
        ctxt: Airflow context
    Notes:
        Creation of new HCIO endpoints is handled via GH actions in avant-data-gitops
        # TODO: instructions for that here or in gitops repo?
    """

    config: ConfigParser = ctxt['config']
    ...



def hello_world():
    print("Hello, World!")
    time.sleep(5)


with DAG(
    dag_id="hello_world_dag",
    start_date=datetime(2021, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    # on_failure_callback=RuntimeHook().on_failure_callback,
    # on_success_callback=RuntimeHook().on_success_callback,
) as dag:

    task0 = EmptyOperator(task_id="id0")
    task1 = PythonOperator(task_id="hello_world", python_callable=hello_world, on_execute_callback=hcio_task_alert)
    task2 = PythonOperator(task_id="hello_world2", python_callable=hello_world)
    hcio = PythonOperator(task_id="hcio", python_callable=hcio_dag_alert, op_kwargs={'slug':'data-80123'})

    task0 >> task1 >> task2
