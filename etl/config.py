"""Configuration du pipeline ETL BAAC."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    baac_dir: Path
    insee_file: Path
    sql_dir: Path
    start_year: int
    end_year: int
    database_url: str
    dry_run: bool


def _as_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "oui"}


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[1]
    baac_dir = Path(os.getenv("BAAC_DATA_DIR", project_root / "data/raw/baac"))
    insee_dir = Path(os.getenv("INSEE_DATA_DIR", project_root / "data/raw/insee"))
    insee_file = insee_dir / "ref_geographie_2024_population_2022.csv"
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))
    name = os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "baac_dw"))
    user = os.getenv("DB_USER", os.getenv("POSTGRES_USER", "baac_user"))
    password = os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "change_me_local_only"))
    return Settings(
        project_root=project_root,
        baac_dir=baac_dir,
        insee_file=insee_file,
        sql_dir=project_root / "sql",
        start_year=int(os.getenv("BAAC_START_YEAR", "2019")),
        end_year=int(os.getenv("BAAC_END_YEAR", "2024")),
        database_url=os.getenv("DATABASE_URL", f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"),
        dry_run=_as_bool(os.getenv("ETL_DRY_RUN")),
    )

