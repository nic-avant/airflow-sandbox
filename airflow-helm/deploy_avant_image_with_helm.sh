# docker pull avant.jfrog.io/shared-images/avant-airflow:dev
helm repo add apache-airflow https://airflow.apache.org/
helm repo update
kubectl create namespace airflow
kubectl apply -f ./airflow-volume.yml
# helm install airflow apache-airflow/airflow --version 1.6.0 -f values.yaml
helm upgrade \
    --install airflow apache-airflow/airflow \
    --namespace airflow \
    --version 1.11.0 \
    -f values.yaml \
    \
    --set dagProcessor.enabled=true \
    \
    --wait=true # --set images.airflow.repository=avant.jfrog.io/shared-images/avant-airflow \
    # --set images.airflow.tag=dev \
    # --set webserver.replicas=1 \
    # --set triggerer.replicas=1 \
    # --set scheduler.replicas=1 \
