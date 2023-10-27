# docker pull avant.jfrog.io/shared-images/avant-airflow:dev
# helm repo add apache-airflow https://airflow.apache.org/
# helm repo update
# helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace
# kubectl apply -f ./airflow-volume.yml
helm upgrade airflow apache-airflow/airflow \
    --namespace airflow \
    --version 1.11.0 \
    -f values.yml \
    --wait=false
# --set dagProcessor.enabled=true \
