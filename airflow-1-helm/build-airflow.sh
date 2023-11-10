#!/bin/bash
docker build -t airflow:1.10.15-api-enabled .
# I'm using minikube as k8s cluster and I need to load tihs image into the image cache
minikube -p slice image load airflow:1.10.15-api-enabled
