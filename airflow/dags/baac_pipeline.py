"""Orchestration du chargement du Data Warehouse BAAC."""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "baac",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="baac_datawarehouse_pipeline",
    description="Extraction, transformation, qualité et chargement des données BAAC",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["baac", "data-warehouse", "school-project"],
) as dag:
    verifier_sources = BashOperator(
        task_id="verifier_sources",
        bash_command=(
            "test -d /opt/airflow/project/data/raw/baac && "
            "test -d /opt/airflow/project/data/raw/insee && "
            "find /opt/airflow/project/data/raw/baac -name '*.csv' -print -quit | grep -q ."
        ),
    )

    tester_transformations = BashOperator(
        task_id="tester_transformations",
        bash_command="cd /opt/airflow/project && python -m pytest -q tests",
    )

    charger_entrepot = BashOperator(
        task_id="charger_entrepot",
        bash_command=(
            "cd /opt/airflow/project && python -m etl.run_pipeline "
            "--start-year {{ dag_run.conf.get('start_year', var.value.get('baac_start_year', '2019')) }} "
            "--end-year {{ dag_run.conf.get('end_year', var.value.get('baac_end_year', '2024')) }}"
        ),
    )

    publier_vues = BashOperator(
        task_id="publier_vues_analytiques",
        bash_command=(
            "for f in /opt/airflow/project/sql/analytics/[0-9][0-9]_*.sql; do "
            "PGPASSWORD=\"$DB_PASSWORD\" psql -v ON_ERROR_STOP=1 -h \"$DB_HOST\" -p \"$DB_PORT\" "
            "-U \"$DB_USER\" -d \"$DB_NAME\" -f \"$f\"; done"
        ),
    )

    verifier_sources >> tester_transformations >> charger_entrepot >> publier_vues
