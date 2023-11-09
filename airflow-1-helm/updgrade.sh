#!/bin/bash

# set the release-name & namespace
export AIRFLOW_NAME="airflow-1-cluster"
export AIRFLOW_NAMESPACE="airflow-1-cluster"
helm upgrade \
    "$AIRFLOW_NAME" \
    airflow-stable/airflow \
    --namespace "$AIRFLOW_NAMESPACE" \
    --version "8.8.0" \
    --values ./custom-values.yaml
