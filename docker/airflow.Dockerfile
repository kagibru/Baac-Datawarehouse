FROM apache/airflow:2.10.5-python3.12

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*
USER airflow

COPY requirements.txt /tmp/baac-requirements.txt
RUN pip install --no-cache-dir -r /tmp/baac-requirements.txt

ENV PYTHONPATH=/opt/airflow/project
