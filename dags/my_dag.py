"hello world airflow dag"
from datetime import datetime

from airflow.operators.python import PythonOperator

from airflow import DAG

from airflow.hooks.base_hook import BaseHook
# import pdpyras
import os


class RuntimeHook(BaseHook):
    """Hook for runtime actions"""

    avant_conn_name = "avant_pagerduty"

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.foo = 'foo'

    def on_failure_callback(self, ctx, **kwargs):
        return self._invoke(
            '1', '2', '3', '4', '5'
        )

    def on_success_callback(self, ctx, **kwargs):
        return self._invoke(
            '1', '2', '3', '4', '5'
        )

    def _invoke(self, dag_id, run_id, task_id, log_url, action):
        print('INVOKED THE RUNTIMEHOOK')


def hello_world():
    print("Hello, World!")

with DAG(
    dag_id="hello_world_dag",
    start_date=datetime(2021, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    on_failure_callback=RuntimeHook().on_failure_callback,
    on_success_callback=RuntimeHook().on_success_callback,
) as dag:
    task1 = PythonOperator(task_id="hello_world", python_callable=hello_world)

    task1
