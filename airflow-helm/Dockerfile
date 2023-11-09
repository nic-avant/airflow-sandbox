FROM apache/airflow
COPY . /opt/airflow/dags
RUN pip install --no-cache-dir apache-airflow-providers-databricks
RUN pip install --extra-index-url https://pypi.services.global.avant.com/simple avant-dag-tools==0.0.37
RUN pip install dbt-core
RUN pip install 'astronomer-cosmos[dbt-databricks]'

