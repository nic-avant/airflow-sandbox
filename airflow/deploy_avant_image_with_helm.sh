docker pull avant.jfrog.io/shared-images/avant-airflow:dev
helm repo add apache-airflow https://airflow.apache.org/
helm repo update
kubectl apply -f ./airflow-volume.yml
helm upgrade airflow apache-airflow/airflow \
    --namespace default \
    --version 1.6.0 -f ./values.yml \
    --set images.airflow.repository=avant.jfrog.io/shared-images/avant-airflow \
    --set images.airflow.tag=dev \
    --wait=false
