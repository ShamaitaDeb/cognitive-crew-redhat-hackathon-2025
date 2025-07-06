FROM apache/airflow:slim-2.8.2-python3.9
USER airflow
WORKDIR /opt/airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/opt/airflow"

COPY ./src ./src
COPY ./dags ./dags
COPY ./test ./test

COPY entrypoint.sh /entrypoint.sh

USER root
RUN chmod 777 /entrypoint.sh

USER airflow
# Expose the necessary ports
EXPOSE 8080 5555 8793

ENTRYPOINT ["/entrypoint.sh"]