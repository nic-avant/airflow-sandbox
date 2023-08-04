"hello world airflow dag"
from datetime import datetime

from airflow.operators.python import PythonOperator

from airflow import DAG

from airflow.hooks.base_hook import BaseHook

from airflow.operators.empty import EmptyOperator
import requests

# I think this is all that really needs to be configured...
PROJECT_PING_KEY = "844d7hQguj_-hZ26ByMAeA"
SLUG = "data-80123"
URL =f"https://hc-ping.com/{PROJECT_PING_KEY}/{SLUG}"
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

    def hcio_alert(self, action: str):
        # hcio alert
        requests.get(URL if action=='resolve' else URL + "/fail")

    def _invoke(self, dag_id, run_id, task_id, log_url, action):
        # severity can be critical, error, warning or info
        if action not in ('trigger', 'resolve'):
            raise ValueError("action must be 'trigger' or 'resolve'")

        self.hcio_alert(action)
        print('Triggering a dag')


def hello_world():
    # raise ValueError()
    print("Hello, World!")


with DAG(
    dag_id="hello_world_dag",
    start_date=datetime(2021, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    on_failure_callback=RuntimeHook().on_failure_callback,
    on_success_callback=RuntimeHook().on_success_callback,
) as dag:

    task0 = EmptyOperator(task_id="id0")
    task1 = PythonOperator(task_id="hello_world", python_callable=hello_world)

    task0 >> task1
