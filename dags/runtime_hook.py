from airflow.hooks.base_hook import BaseHook
import pdpyras
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
        print(dag_id)
