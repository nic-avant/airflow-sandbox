#!/bin/bash
## add this helm repository
helm repo add airflow-stable https://airflow-helm.github.io/charts

## update your helm repo cache
helm repo update

## set the release-name & namespace
export AIRFLOW_NAME="airflow-1-cluster"
export AIRFLOW_NAMESPACE="airflow-1-cluster"

## create the namespace
kubectl create ns "$AIRFLOW_NAMESPACE"

## install using helm 3
helm install \
    "$AIRFLOW_NAME" \
    airflow-stable/airflow \
    --namespace "$AIRFLOW_NAMESPACE" \
    --version "8.8.0" \
    --values ./custom-values.yaml

## wait until the above command returns and resources become ready
## (may take a while)
