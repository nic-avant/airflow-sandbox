import requests
from airflow.models import Variable
from airflow.configuration import ConfigParser
# # This needs to be configurable per DAG or per Task????
# SLUG = "data-80123"
#
# # TODO: add avant_hcio airflow connection
# avant_hcio_conn_name = "avant_hcio"
#
# avant_hcio_conn = self.get_connection(self.avant_hcio_conn_name)
# # TODO: obviously fix this
# # Airflow connections are configured in UI for campaign
# self.hcio_project_ping_key = avant_hcio_conn.extra_dejson.get('PROJECT_PING_KEY or Password')
# self.hcio_url =f"https://hc-ping.com/{self.hcio_project_ping_key}/{SLUG}"
#
#
# def hcio_alert(self, action: Optional[str], *, override: str):
#
#     """Issue ping to healthcheck.io
#
#     Args:
#         action: Flag for PagerDuty action used by hcio_alert to configure
#         whether or not to ping successfully or to the /fail endpoint
#     """
#     if action=='fail':
#         requests.get(self.hcio_url + "/fail")
#         return None
#     # TODO: need to configure self.hcio_url and then in _invoke call this
#     # function appropriately based on action as well as if an exception was
#     # caught -> that should result in hcio /fail call
#     requests.get(self.hcio_url if action=='resolve' else self.hcio_url + "/fail")
#
# def myfunc(slug: str) -> None:
#     ...
#
# hcio_task = PythonOperator(
# dag=DAG_DEFINATION,
# task_id="hcio_task",
# python_callable=myfunc,
# provide_context=True,
# op_kwargs={'slug': "SLUG"}
# )
# hcio_task.set_upstream(parent_task_id)
#
def hcio_task_alert_callback_base(ctxt: dict, slug: str, success: bool):
    """
    Base function for engineers to use and wrap to implement hcio in task callbacks
    Args:
        ctxt: Airflow context
        slug: HCIO slug for healthcheck
        success: Pass True or False in wrapper to have on_success_callback and on_failure_callback
    Notes:
        Creation of new HCIO endpoints is handled via GH actions in avant-data-gitops
        # TODO: instructions for that here or in gitops repo?

    Example:
        >>> # User creates a python function that returns the base hcio task
        >>> # callback function with the appropriate slug as the argument. This
        >>> # needs to be defined manually since Airflow doesn't allow me to pass
        >>> # args/kwargs to callback functions
        >>> # ie. it's a pseudo partial
        >>>
        >>> from hcio import hcio_task_alert_callback_base
        >>>
        >>> def hcio_task_on_success_callback(ctxt: dict):
        >>>     "user-defined function to pass hcio slug to common hcio utility function"
        >>>     slug = "USER PUTS HCIO SLUG HERE"
        >>>     return hcio_task_alert_callback_base(ctxt, slug=slug, success=True)
        >>>
        >>> def hcio_task_on_failure_callback(ctxt: dict):
        >>>     "user-defined function to pass hcio slug to common hcio utility function"
        >>>     slug = "USER PUTS HCIO SLUG HERE"
        >>>     return hcio_task_alert_callback_base(ctxt, slug=slug, success=False)
        >>>
        >>> task = PythonOperator(task_id="hello_world", python_callable=hello_world, on_success_callback=hcio_task_on_success_callback, on_failure_callback=hcio_task_on_failure_callback)
    """
    project_ping_key = Variable.get("HCIO_PROJECT_PING_KEY")
    context = ctxt.get("_context", {})
    config: ConfigParser = context.get( 'conf' )  # noqa: F841
    print(ctxt.__dict__)
    # TODO: I hope that airflow variables are in the config to extract project ping key from
    url =f"https://hc-ping.com/{project_ping_key}/{slug}"
    requests.get(url if success is True else url + "/fail")
