"hello world airflow dag"
import time
from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from airflow.configuration import ConfigParser
from airflow.models import Variable

# TODO: Am I writing this for task or dag level hcio? I think DAG so the task
# level callback is not what I need to do... just a function that takes a slug
# to be tacked onto the end of a DAG in campaign

# TODO: remove default slug value
def hcio_dag_alert(slug: str = 'data-80123', **kwargs):
    """Function to be used a python_callable for DAG Healthcheck with hcio

    Args:
        slug: slug id of hcio endpoint to use - endpoints are to be created in avant-data-gitops repo
        **kwargs: Airflow context
    """
    from airflow.models import Variable
    project_ping_key = Variable.get("HCIO_PROJECT_PING_KEY")
    print("DAG ALERT TASK")
    success = kwargs.get('success', True)
    print(kwargs)

    url =f"https://hc-ping.com/{project_ping_key}/{slug}"
    requests.get(url if success is True else url + "/fail")

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
    from airflow.models import Variable
    project_ping_key = Variable.get("HCIO_PROJECT_PING_KEY")
    context = ctxt.get("_context")
    config: ConfigParser = context['conf']
    print(ctxt.__dict__)
    # TODO: I hope that airflow variables are in the config to extract project ping key from
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

    task1 = PythonOperator(task_id="hello_world", python_callable=hello_world, on_success_callback=hcio_task_on_success_callback, on_failure_callback=hcio_task_on_failure_callback)
    task2 = PythonOperator(task_id="hello_world2", python_callable=hello_world)
    hcio = PythonOperator(task_id="hcio", python_callable=hcio_dag_alert, op_kwargs={'slug':'data-80123'})

    task1 >> task2 >> hcio



{'_context': {'conf': <***.configuration.AirflowConfigParser object at
              0xffff80e8a090>, 'dag': <DAG: hello_world_dag>, 'dag_run':
              <DagRun hello_world_dag @ 2023-08-08 13:55:55.484198+00:00:
              manual__2023-08-08T13:55:55.484198+00:00, state:running,
              queued_at: 2023-08-08 13:55:55.496171+00:00. externally
              triggered: True>, 'data_interval_end': DateTime(2023, 8, 8, 13,
                                                              0, 0,
                                                              tzinfo=Timezone('UTC')),
              'data_interval_start': DateTime(2023, 8, 8, 12, 0, 0,
                                              tzinfo=Timezone('UTC')), 'ds':
              '2023-08-08', 'ds_nodash': '20230808', 'execution_date':
              DateTime(2023, 8, 8, 13, 55, 55, 484198, tzinfo=Timezone('UTC')),
              'expanded_ti_count': None, 'inlets': [], 'logical_date':
              DateTime(2023, 8, 8, 13, 55, 55, 484198, tzinfo=Timezone('UTC')),
              'macros': <module '***.macros' from
              '/home/***/.local/lib/python3.7/site-packages/***/macros/__init__.py'>,
              'next_ds': '2023-08-08', 'next_ds_nodash': '20230808',
              'next_execution_date': DateTime(2023, 8, 8, 13, 55, 55, 484198,
                                              tzinfo=Timezone('UTC')),
              'outlets': [], 'params': {}, 'prev_data_interval_start_success':
              DateTime(2023, 8, 8, 12, 0, 0, tzinfo=Timezone('UTC')),
              'prev_data_interval_end_success': DateTime(2023, 8, 8, 13, 0, 0,
                                                         tzinfo=Timezone('UTC')),
              'prev_ds': '2023-08-08', 'prev_ds_nodash': '20230808',
              'prev_execution_date': DateTime(2023, 8, 8, 13, 55, 55, 484198,
                                              tzinfo=Timezone('UTC')),
              'prev_execution_date_success': DateTime(2023, 8, 8, 13, 54, 41,
                                                      44948,
                                                      tzinfo=Timezone('UTC')),
              'prev_start_date_success': DateTime(2023, 8, 8, 13, 54, 42,
                                                  136548,
                                                  tzinfo=Timezone('UTC')),
              'run_id': 'manual__2023-08-08T13:55:55.484198+00:00', 'task':
              <Task(PythonOperator): hello_world>, 'task_instance':
              <TaskInstance: hello_world_dag.hello_world
              manual__2023-08-08T13:55:55.484198+00:00 [success]>,
              'task_instance_key_str':
              'hello_world_dag__hello_world__20230808', 'test_mode': False,
              'ti': <TaskInstance: hello_world_dag.hello_world
              manual__2023-08-08T13:55:55.484198+00:00 [success]>,
              'tomorrow_ds': '2023-08-09', 'tomorrow_ds_nodash': '20230809',
              'triggering_dataset_events': <Proxy at 0xffff65da5af0 with
              factory <function
              TaskInstance.get_template_context.<locals>.get_triggering_events
              at 0xffff65d84cb0>>, 'ts': '2023-08-08T13:55:55.484198+00:00',
              'ts_nodash': '20230808T135555', 'ts_nodash_with_tz':
              '20230808T135555.484198+0000', 'var': {'json': None, 'value':
                                                     None}, 'conn': None,
              'yesterday_ds': '2023-08-07', 'yesterday_ds_nodash': '20230807',
              'templates_dict': None}, '_deprecation_replacements':
 {'execution_date': ['data_interval_start', 'logical_date'], 'next_ds': ['{{
 data_interval_end | ds }}'], 'next_ds_nodash': ['{{ data_interval_end |
 ds_nodash }}'], 'next_execution_date': ['data_interval_end'], 'prev_ds': [],
                                                 'prev_ds_nodash': [],
  'prev_execution_date': [], 'prev_execution_date_success':
  ['prev_data_interval_start_success'], 'tomorrow_ds': [],
  'tomorrow_ds_nodash': [], 'yesterday_ds': [], 'yesterday_ds_nodash': []}}
