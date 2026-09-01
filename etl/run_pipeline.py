"""Point d'entrée du pipeline ETL BAAC."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import replace

from etl.config import load_settings
from etl.extract import extract_insee, extract_year
from etl.quality import validate
from etl.transform import combine


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construit le Data Warehouse BAAC")
    parser.add_argument("--start-year", type=int)
    parser.add_argument("--end-year", type=int)
    parser.add_argument("--dry-run", action="store_true", help="Transforme et contrôle sans charger PostgreSQL")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s | %(levelname)s | %(message)s")
    args = arguments()
    settings = load_settings()
    settings = replace(settings, start_year=args.start_year or settings.start_year, end_year=args.end_year or settings.end_year, dry_run=args.dry_run or settings.dry_run)
    if settings.start_year > settings.end_year:
        raise SystemExit("BAAC_START_YEAR doit être inférieur ou égal à BAAC_END_YEAR")

    logging.info("Extraction des millésimes %s à %s", settings.start_year, settings.end_year)
    yearly = [extract_year(settings.baac_dir, year) for year in range(settings.start_year, settings.end_year + 1)]
    insee = extract_insee(settings.insee_file)
    logging.info("Transformation et agrégation à la granularité accident")
    frames = combine(yearly, insee, settings.start_year, settings.end_year)
    quality = validate(frames)
    logging.info("Résultat: %s accidents, %s routes, %s circonstances, %s localisations", len(frames.fact_accident), len(frames.dim_route), len(frames.dim_circonstance), len(frames.dim_localisation))
    logging.info("Qualité: %s date(s), %s horaire(s) et %s commune(s) non rattachés", quality.unknown_dates, quality.unknown_times, quality.unknown_localities)
    if settings.dry_run:
        logging.info("Dry-run terminé: aucune écriture dans PostgreSQL")
        return

    from etl.load import create_engine_for, initialize_database, load_warehouse

    logging.info("Connexion à PostgreSQL")
    engine = create_engine_for(settings.database_url)
    initialize_database(engine, settings.sql_dir)
    run_id = load_warehouse(engine, frames)
    logging.info("Chargement terminé avec succès, run_id=%s", run_id)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.exception("Échec du pipeline: %s", error)
        sys.exit(1)
