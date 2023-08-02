from airflow.hooks.base_hook import BaseHook
import pdpyras
import os


class RuntimeHook(BaseHook):
    """Hook for runtime actions"""

    avant_conn_name = "avant_pagerduty"

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        ...
        # avant_conn = self.get_connection(self.avant_conn_name)
        # self.avant_routing_key = avant_conn.extra_dejson.get('Password')
        # print(avant_conn)
        # print(type(avant_conn))
        # print(self.avant_routing_key)

    def on_failure_callback(self, ctx, **kwargs):
        # ti = ctx["task_instance"]
        # run_id = ctx["run_id"]
        return self._invoke(
            '1', '2', '3', '4', '5'
            # dag_id=ti.dag_id,
            # run_id=run_id,
            # task_id=ti.task_id,
            # log_url=ti.log_url,
            # action="trigger"
        )

    def on_success_callback(self, ctx, **kwargs):
        # ti = ctx["task_instance"]
        # run_id = ctx["run_id"]
        return self._invoke(
            '1', '2', '3', '4', '5'
            # dag_id=ti.dag_id,
            # run_id=run_id,
            # task_id=ti.task_id,
            # log_url=ti.log_url,
            # action="resolve"
        )

    def _invoke(self, dag_id, run_id, task_id, log_url, action):
        print(f"{dag_id=}")
        print(f"{run_id=}")
        print(f"{task_id=}")
        print(f"{log_url=}")
        print(f"{action=}")
        # # severity can be critical, error, warning or info
        # if action not in ('trigger', 'resolve'):
        #     raise ValueError("action must be 'trigger' or 'resolve'")
        #
        # dedup_key = str(hash(dag_id + run_id + task_id))
        # base_message = f' incident event in Avant PagerDuty for dag_id={dag_id} and run_id={run_id}'
        #
        # try:
        #     events_session = pdpyras.EventsAPISession(self.avant_routing_key)
        #     if action == 'trigger':
        #         print('Triggering ' + base_message)
        #         message = """
        #         Avant PagerDuty: {} Airflow Campaign Partner01 DAG '{}' failed on task '{}'.
        #         See Airflow logs for run_id='{}'
        #         """.format(
        #             'TEST',
        #             dag_id,
        #             task_id,
        #             run_id
        #         )
        #         details = {
        #             "dag": dag_id,
        #             "task": task_id,
        #             "run": run_id
        #         }
        #         events_session.trigger(summary=message,
        #                                source='Airflow Campaign Partner01',
        #                                severity='warning',
        #                                dedup_key=dedup_key,
        #                                links=[{'href': log_url}],
        #                                custom_details=details)
        #     else:
        #         print('Resolving ' + base_message)
        #         events_session.resolve(dedup_key)
        #     print(f'Successfully executed PagerDuty action={action}')
        #
        # except Exception as e:
        #     print(e)
