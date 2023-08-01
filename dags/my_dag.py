"hello world airflow dag"
from datetime import datetime

from airflow.operators.python import PythonOperator

from airflow import DAG


def hello_world():
    print("Hello, World!")


with DAG(
    dag_id="hello_world_dag",
    start_date=datetime(2021, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
) as dag:
    task1 = PythonOperator(task_id="hello_world", python_callable=hello_world)

    task1
