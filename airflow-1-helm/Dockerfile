FROM apache/airflow:1.10.15-python3.7
# Set the working directory in the container to /airflow
WORKDIR /airflow

# Set AIRFLOW_HOME
ENV AIRFLOW_HOME=/airflow

# Install Airflow
# RUN pip install apache-airflow==1.10.15

# Create the airflow.cfg file
RUN echo "[api]" > ${AIRFLOW_HOME}/airflow.cfg && \
    echo "auth_backend = airflow.api.auth.backend.default" >> ${AIRFLOW_HOME}/airflow.cfg && \
    echo "enable_experimental_api = True" >> ${AIRFLOW_HOME}/airflow.cfg

# Expose port 8080 for the Airflow web server to be accessible from the outside
EXPOSE 8080

# Start the web server on port 8080
CMD ["airflow", "webserver", "-p", "8080"]
