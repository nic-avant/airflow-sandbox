"hello world airflow dag"
import time
from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from hcio import hcio_task_alert_callback_base

from airflow.configuration import AirflowConfigParser


# TODO: remove default slug value
def hcio_task(slug: str = 'data-80123', **kwargs):
    """Function to be used a python_callable for task to issue hcio pings

    Args:
        slug: slug id of hcio endpoint to use - endpoints are to be created in avant-data-gitops repo
        **kwargs: Airflow context
    """
    from airflow.models import Variable
    project_ping_key = Variable.get("HCIO_PROJECT_PING_KEY")
    print("HCIO TASK")
    # Not sure if this is really useful
    success = kwargs.get('success', True)
    # Can extract data from the conf if we want to post arbitrary data to an hcio endpoint
    conf: AirflowConfigParser = kwargs.get('conf')  # noqa: F841

    url =f"https://hc-ping.com/{project_ping_key}/{slug}"
    requests.get(url if success is True else url + "/fail")


def hcio_task_on_success_callback(ctxt: dict):
    """ user-defined function to pass hcio slug to common hcio utility function """
    slug = "data-80123"
    print("TASK ON SUCCESS CALLBACK")
    return hcio_task_alert_callback_base(ctxt, slug=slug, success=True)

def hcio_task_on_failure_callback(ctxt: dict):
    """ user-defined function to pass hcio slug to common hcio utility function """
    slug = "data-80123"
    print("TASK ON FAILURE CALLBACK")
    return hcio_task_alert_callback_base(ctxt, slug=slug, success=False)


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

    task1 = PythonOperator(task_id="hello_world",
                           python_callable=hello_world,
                           on_success_callback=hcio_task_on_success_callback,
                           on_failure_callback=hcio_task_on_failure_callback)
    task2 = PythonOperator(task_id="hello_world2", python_callable=hello_world)
    hcio = PythonOperator(task_id="hcio", python_callable=hcio_task, op_kwargs={'slug':'data-80123'})

    task1 >> task2 >> hcio
