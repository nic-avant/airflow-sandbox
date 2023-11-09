#!/bin/bash

# set the release-name & namespace
export AIRFLOW_NAME="airflowone"
export AIRFLOW_NAMESPACE="airflowone"
helm upgrade \
    "$AIRFLOW_NAME" \
    airflow-stable/airflow \
    --namespace "$AIRFLOW_NAMESPACE" \
    --version "8.8.0" \
    --values ./custom-values.yaml
