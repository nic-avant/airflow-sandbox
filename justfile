#!/usr/bin/env just --justfile

build-dag-pauser:
  cd /Users/npayne81/work/airflow-sandbox/PauseRunningAirflow1Dags && sam build --use-container  && cd -

test-dag-pauser:
  cd /Users/npayne81/work/airflow-sandbox/PauseRunningAirflow1Dags && sam local invoke --docker-network host  && cd -

build-and-test-dag-pauser: build-dag-pauser test-dag-pauser

test-dag-pauser-locally:
    echo "Testing Airflow API running python locally"
    /Users/npayne81/work/airflow-sandbox/.venv/airflow-sandbox/bin/python /Users/npayne81/work/airflow-sandbox/PauseRunningAirflow1Dags/pause_airflow_dags/app.py

test-dag-pauser-k8s-cron-locally:
    echo "Test app.py for cronjob"
    /Users/npayne81/work/airflow-sandbox/.venv/airflow-sandbox/bin/python /Users/npayne81/work/airflow-sandbox/PauseRunningAirflow1DagsK8Cron/app.py
