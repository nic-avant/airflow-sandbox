#!/bin/bash

helm upgrade \
    airflow apache-airflow/airflow \
    --namespace airflow \
    --version 1.11.0 \
    -f values.yaml \
    --wait=true
