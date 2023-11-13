#!/bin/bash

helm upgrade \
    "airflowone" \
    airflow-stable/airflow \
    --namespace "airflowone" \
    --version "8.8.0" \
    --values ./custom-values.yaml
