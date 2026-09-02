"""Chargement transactionnel des dimensions et de la table de faits."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from etl.transform import WarehouseFrames


def create_engine_for(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def execute_sql_file(connection: Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    for statement in (part.strip() for part in sql.split(";")):
        if statement and not statement.startswith("\\"):
            connection.execute(text(statement))


def initialize_database(engine: Engine, sql_dir: Path) -> None:
    paths = [
        sql_dir / "init/00_create_schemas.sql",
        sql_dir / "ddl/01_create_dimensions.sql",
        sql_dir / "ddl/02_create_fact_accident.sql",
        sql_dir / "ddl/03_create_audit_tables.sql",
        sql_dir / "ddl/04_seed_unknown_members.sql",
    ]
    with engine.begin() as connection:
        for path in paths:
            execute_sql_file(connection, path)


def run_quality_checks(engine: Engine, sql_dir: Path) -> None:
    with engine.begin() as connection:
        execute_sql_file(connection, sql_dir / "quality/01_run_quality_checks.sql")


def _upsert_table(connection: Connection, frame: pd.DataFrame, table: str, natural_key: str) -> None:
    temporary = f"tmp_{table}"
    frame.to_sql(temporary, connection, schema="staging", if_exists="replace", index=False, method="multi", chunksize=2000)
    columns = list(frame.columns)
    quoted = ", ".join(f'"{column}"' for column in columns)
    updates = ", ".join(f'"{column}" = EXCLUDED."{column}"' for column in columns if column != natural_key)
    connection.execute(text(f'INSERT INTO dw."{table}" ({quoted}) SELECT {quoted} FROM staging."{temporary}" WHERE true ON CONFLICT ("{natural_key}") DO UPDATE SET {updates}'))
    connection.execute(text(f'DROP TABLE staging."{temporary}"'))


def load_warehouse(engine: Engine, frames: WarehouseFrames, pipeline_name: str = "baac_2019_2024") -> int:
    with engine.begin() as connection:
        run_id = connection.execute(
            text("INSERT INTO audit.etl_run (pipeline_name, start_year, end_year) VALUES (:name, :start, :end) RETURNING run_id"),
            {"name": pipeline_name, "start": int(frames.fact_accident["millesime_source"].min()), "end": int(frames.fact_accident["millesime_source"].max())},
        ).scalar_one()
        _upsert_table(connection, frames.dim_date, "dim_date", "date_key")
        _upsert_table(connection, frames.dim_horaire, "dim_horaire", "horaire_key")
        _upsert_table(connection, frames.dim_localisation, "dim_localisation", "code_commune")
        _upsert_table(connection, frames.dim_route, "dim_route", "route_profile_code")
        _upsert_table(connection, frames.dim_circonstance, "dim_circonstance", "circonstance_profile_code")

        fact = frames.fact_accident.copy()
        lookups = {
            "localisation_key": ("dim_localisation", "code_commune"),
            "route_key": ("dim_route", "route_profile_code"),
            "circonstance_key": ("dim_circonstance", "circonstance_profile_code"),
        }
        for target, (table, natural) in lookups.items():
            mapping = pd.read_sql(text(f'SELECT "{natural}", "{target}" FROM dw."{table}"'), connection).set_index(natural)[target]
            fact[target] = fact[natural].map(mapping).fillna(0).astype(int)
        fact_columns = ["num_acc", "date_key", "horaire_key", "localisation_key", "route_key", "circonstance_key", "accident_count", "nombre_vehicules", "nombre_usagers", "nombre_victimes", "nombre_indemnes", "nombre_tues", "nombre_blesses_hospitalises", "nombre_blesses_legers", "nombre_conducteurs", "nombre_passagers", "nombre_pietons", "nombre_vehicules_legers", "nombre_deux_roues", "nombre_poids_lourds", "nombre_lieux_associes", "est_accident_mortel", "est_multi_voies", "adresse", "voie_principale", "latitude", "longitude", "millesime_source"]
        _upsert_table(connection, fact[fact_columns], "fact_accident", "num_acc")

        for object_name, count in frames.source_volumes.items():
            connection.execute(text("INSERT INTO audit.etl_volume (run_id, stage_name, object_name, row_count) VALUES (:run_id, 'EXTRACT', :name, :count)"), {"run_id": run_id, "name": object_name, "count": count})
        connection.execute(text("INSERT INTO audit.etl_volume (run_id, stage_name, object_name, row_count) VALUES (:run_id, 'LOAD', 'dw.fact_accident', :count)"), {"run_id": run_id, "count": len(fact)})
        connection.execute(text("UPDATE audit.etl_run SET status='SUCCESS', finished_at=current_timestamp, message=:message WHERE run_id=:run_id"), {"run_id": run_id, "message": f"{len(fact)} accidents chargés"})
        return int(run_id)
