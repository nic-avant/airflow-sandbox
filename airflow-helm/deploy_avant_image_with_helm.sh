# Comment/Uncomment this out to pull the latest dev image from Avant's artifactory
docker pull avant.jfrog.io/shared-images/avant-airflow:dev
helm repo add apache-airflow https://airflow.apache.org/
helm repo update
kubectl create namespace airflow
kubectl apply -f ./airflow-volume.yml
helm install \
    airflow apache-airflow/airflow \
    --namespace airflow \
    --version 1.11.0 \
    -f values.yaml \
    --set dagProcessor.enabled=true \
    --wait=true
