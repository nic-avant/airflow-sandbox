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

deploy-airflow1:
    cd /Users/npayne81/work/airflow-sandbox/airflow-1-helm/  && \
    bash deploy_airflow1.sh && \
    cd -

deploy-airflow2:
    cd /Users/npayne81/work/airflow-sandbox/airflow-helm/  && \
    bash deploy_avant_image_with_helm.sh && \
    cd -

deploy-cronjob:
    cd /Users/npayne81/work/airflow-sandbox/PauseRunningAirflow1DagsK8Cron  && \
    kubectl create configmap app-script --from-file=app.py && \
    kubectl create -f job/cronjob.yml && \
    cd -
