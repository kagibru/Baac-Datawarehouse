"""Extraction et harmonisation technique des fichiers CSV sources."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


FILE_PATTERNS = {
    "caracteristiques": ("caract", "caracteristiques", "carcteristiques"),
    "lieux": ("lieux",),
    "vehicules": ("vehicules",),
    "usagers": ("usagers",),
}


def normalize_column(name: str) -> str:
    value = unicodedata.normalize("NFKD", str(name).lstrip("\ufeff"))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def read_csv_text(path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            frame = pd.read_csv(path, sep=";", dtype=str, encoding=encoding, keep_default_na=False, na_values=[], low_memory=False)
            frame.columns = [normalize_column(column) for column in frame.columns]
            return frame
        except UnicodeDecodeError as error:
            last_error = error
    raise ValueError(f"Encodage illisible pour {path}") from last_error


def find_source_file(directory: Path, dataset: str, year: int) -> Path:
    candidates = []
    for path in directory.glob(f"*{year}*.csv"):
        stem = normalize_column(path.stem)
        if any(stem.startswith(prefix) for prefix in FILE_PATTERNS[dataset]):
            candidates.append(path)
    if len(candidates) != 1:
        raise FileNotFoundError(f"Une source {dataset} {year} était attendue, {len(candidates)} trouvée(s): {[path.name for path in candidates]}")
    return candidates[0]


def extract_year(directory: Path, year: int) -> dict[str, pd.DataFrame]:
    extracted: dict[str, pd.DataFrame] = {}
    for dataset in FILE_PATTERNS:
        path = find_source_file(directory, dataset, year)
        frame = read_csv_text(path)
        if "accident_id" in frame.columns and "num_acc" not in frame.columns:
            frame = frame.rename(columns={"accident_id": "num_acc"})
        if "num_acc" not in frame.columns:
            raise ValueError(f"Colonne Num_Acc absente de {path.name}")
        frame["source_year"] = year
        frame["source_file"] = path.name
        frame["source_row_number"] = range(2, len(frame) + 2)
        extracted[dataset] = frame
    return extracted


def extract_insee(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Référentiel INSEE absent: {path}")
    return read_csv_text(path)

