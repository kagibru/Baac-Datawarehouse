"""Vérifie que les sources nécessaires sont présentes et lisibles."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from etl.extract import FILE_PATTERNS, find_source_file, read_csv_text

BAAC = Path("data/raw/baac")
INSEE = Path("data/raw/insee/ref_geographie_2024_population_2022.csv")

errors = []
for year in range(2019, 2025):
    for dataset in FILE_PATTERNS:
        try:
            path = find_source_file(BAAC, dataset, year)
            frame = read_csv_text(path)
            if "num_acc" not in frame.columns and "accident_id" not in frame.columns:
                errors.append(f"{path}: identifiant accident absent")
        except Exception as error:
            errors.append(str(error))

if not INSEE.exists():
    errors.append(f"Référentiel absent: {INSEE}")

if errors:
    raise SystemExit("\n".join(f"ERREUR {item}" for item in errors))
print("OK: 24 fichiers BAAC et référentiel INSEE disponibles")
