"hello world airflow dag"
from datetime import datetime

from airflow.operators.python import PythonOperator

from airflow import DAG

from airflow.hooks.base_hook import BaseHook

from airflow.operators.empty import EmptyOperator
import requests

URL ="https://hc-ping.com/844d7hQguj_-hZ26ByMAeA/data-80123"
class RuntimeHook(BaseHook):
    """Hook for runtime event handling"""

    avant_conn_name = "avant_pagerduty"

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.foo = 'foo'

    def on_failure_callback(self, ctx, **kwargs):
        ti = ctx["task_instance"]
        run_id = ctx["run_id"]
        return self._invoke(
            dag_id=ti.dag_id,
            run_id=run_id,
            task_id=ti.task_id,
            log_url=ti.log_url,
            action="trigger"
        )

    def on_success_callback(self, ctx, **kwargs):
        ti = ctx["task_instance"]
        run_id = ctx["run_id"]
        return self._invoke(
            dag_id=ti.dag_id,
            run_id=run_id,
            task_id=ti.task_id,
            log_url=ti.log_url,
            action="resolve"
        )


    def _invoke(self, dag_id, run_id, task_id, log_url, action):
        # severity can be critical, error, warning or info
        if action not in ('trigger', 'resolve'):
            raise ValueError("action must be 'trigger' or 'resolve'")
        # hcio alert
        requests.get(URL if action=='resolve' else URL + "/fail")

        print('Triggering a dag')

def alert_me_dammit(ctxt):
    print('------------------------------------------')
    print('------------------------------------------')
    print(f"DAG has succeeded, run_id: {ctxt['run_id']}")
    print('------------------------------------------')
    print('------------------------------------------')
    print(f"{ctxt}")
    print('------------------------------------------')
    print('------------------------------------------')

def hello_world():
    print("Hello, World!")


with DAG(
    dag_id="hello_world_dag",
    start_date=datetime(2021, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    on_failure_callback=RuntimeHook().on_failure_callback,
    # on_success_callback=RuntimeHook().on_success_callback,
    on_success_callback=alert_me_dammit,
) as dag:

    task0 = EmptyOperator(task_id="id0")
    task1 = PythonOperator(task_id="hello_world", python_callable=hello_world)

    task0 >> task1
