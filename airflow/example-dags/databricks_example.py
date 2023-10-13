"""
A trivial DAG used to test DatabricksSubmitRunOperator()
ticket: https://avantinc.atlassian.net/browse/DATA-70023
ref: https://airflow.apache.org/docs/apache-airflow/1.10.12/_api/airflow/contrib/operators/databricks_operator/index.html
"""

from airflow.contrib.operators.databricks_operator import DatabricksSubmitRunOperator
from airflow.utils.dates import days_ago
from airflow.models import DAG

DAG_ID = "databricks_demo__source_git__compute_existing_2"
DATABRICKS_CONN_ID = "databricks"  # created connection in Airflow UI using Databricks token
DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "retries": 0,
}
EXISTING_CLUSTER_ID = "0130-015246-bwnfr1ml"  # "Evelyn Stamey's Cluster"
ROOT_NOTEBOOK_PATH = "data_69221/notebooks"

with DAG(
    dag_id=DAG_ID,
    schedule_interval=None,
    default_args=DEFAULT_ARGS,
) as dag:
    notebook_name = "read_data"
    my_task = DatabricksSubmitRunOperator(
        task_id=notebook_name,
        databricks_conn_id=DATABRICKS_CONN_ID,
        existing_cluster_id=EXISTING_CLUSTER_ID,
        run_name=f"{DAG_ID}__{notebook_name}",
        git_source={
            "git_url": "https://github.com/AvantFinCo/avant-data-platform-testing",
            "git_provider": "gitHub",
            "git_branch": "master"
        },
        notebook_task={
            "notebook_path": f"{ROOT_NOTEBOOK_PATH}/{notebook_name}",
            "source": "GIT",
        },
    )

    my_task