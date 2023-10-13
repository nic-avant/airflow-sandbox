"module for hcio integration"
import requests


def get_project_ping_key():
    # from airflow.models import Variable
    # return Variable.get("HCIO_PROJECT_PING_KEY")
    # TODO: doing this just for exploring hcio
    PROJECT_PING_KEY = '844d7hQguj_-hZ26ByMAeA'
    return PROJECT_PING_KEY


def hcio_task_alert_callback_base(ctxt: dict, slug: str, success: bool):
    """
    Base function for engineers to use and wrap to implement hcio in task callbacks

    The idea is that data engineers can use hcio for fine-grained monitoring of
    tasks via Airflow callbacks. If an engineer wants to simply add a task at
    the end of a DAG to ping an hcio endpoint they should use the HcioAlert
    class in dag_template

    Args:
        ctxt: Airflow context
        slug: HCIO slug for healthcheck
        success: Pass True or False in wrapper to configure a sane on_success_callback and on_failure_callback

    Notes:
        Creation of new HCIO endpoints is handled in avant-data-gitops repository on Github

    Example:
        >>> # User creates a python function that returns the base hcio task
        >>> # callback function with the appropriate slug as the argument. This
        >>> # needs to be defined manually since Airflow doesn't allow me to pass
        >>> # args/kwargs to callback functions
        >>> # ie. it's a pseudo partial

        >>> from hcio import hcio_task_alert_callback_base

        >>> def hcio_task_on_success_callback(ctxt: dict):
        >>>     "user-defined function to pass hcio slug to common hcio utility function"
        >>>     slug = "USER PUTS HCIO SLUG HERE"
        >>>     return hcio_task_alert_callback_base(ctxt, slug=slug, success=True)

        >>> def hcio_task_on_failure_callback(ctxt: dict):
        >>>     "user-defined function to pass hcio slug to common hcio utility function"
        >>>     slug = "USER PUTS HCIO SLUG HERE"
        >>>     return hcio_task_alert_callback_base(ctxt, slug=slug, success=False)

        >>> task = PythonOperator(task_id="hello_world", python_callable=hello_world, on_success_callback=hcio_task_on_success_callback, on_failure_callback=hcio_task_on_failure_callback)
    """
    project_ping_key = get_project_ping_key()
    url =f"https://hc-ping.com/{project_ping_key}/{slug}"
    r = requests.get(url if success is True else url + "/fail")
    return r
