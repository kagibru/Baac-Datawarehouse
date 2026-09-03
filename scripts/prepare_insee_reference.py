"""Construit le référentiel géographique attendu par l'ETL."""

from __future__ import annotations

import argparse
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

COG_URL = "https://www.insee.fr/fr/statistiques/fichier/7766585/cog_ensemble_2024_csv.zip"
POP_URL = "https://www.insee.fr/fr/statistiques/fichier/8290591/populations_reference_2022.zip"


def obtain(source: str | None, url: str, target: Path) -> Path:
    if source:
        return Path(source)
    request = urllib.request.Request(url, headers={"User-Agent": "baac-datawarehouse-school-project/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as output:
        output.write(response.read())
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cog-zip", help="Archive COG déjà téléchargée")
    parser.add_argument("--population-zip", help="Archive populations déjà téléchargée")
    parser.add_argument("--output", type=Path, default=Path("data/raw/insee/ref_geographie_2024_population_2022.csv"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temporary_name:
        temporary = Path(temporary_name)
        cog_zip = obtain(args.cog_zip, COG_URL, temporary / "cog.zip")
        pop_zip = obtain(args.population_zip, POP_URL, temporary / "population.zip")
        with zipfile.ZipFile(cog_zip) as archive:
            archive.extractall(temporary / "cog")
        with zipfile.ZipFile(pop_zip) as archive:
            archive.extractall(temporary / "population")

        cog = temporary / "cog"
        pop = temporary / "population"
        communes = pd.read_csv(cog / "v_commune_2024.csv", dtype=str)
        departements_raw = pd.read_csv(cog / "v_departement_2024.csv", dtype=str)
        regions = pd.read_csv(cog / "v_region_2024.csv", dtype=str)
        populations = pd.read_csv(pop / "donnees_communes.csv", sep=";", dtype=str)
        communes_comer = pd.read_csv(cog / "v_commune_comer_2024.csv", dtype=str)
        history = pd.read_csv(cog / "v_commune_depuis_1943.csv", dtype=str)

        communes = communes[communes["TYPECOM"].isin(["COM", "ARM"])].copy()
        departments = departements_raw[["DEP", "LIBELLE"]].rename(columns={"LIBELLE": "DEPARTEMENT"})
        departments_regions = departements_raw[["DEP", "REG", "LIBELLE"]].rename(columns={"LIBELLE": "DEPARTEMENT"})
        regions = regions[["REG", "LIBELLE"]].rename(columns={"LIBELLE": "REGION"})
        populations = populations[["COM", "PMUN", "PCAP", "PTOT"]]
        current = communes[["COM", "DEP", "REG", "TYPECOM", "COMPARENT", "LIBELLE"]].rename(columns={"LIBELLE": "COMMUNE"})

        comer = communes_comer[["COM_COMER", "COMER", "LIBELLE_COMER", "LIBELLE"]].rename(
            columns={"COM_COMER": "COM", "COMER": "DEP", "LIBELLE_COMER": "DEPARTEMENT", "LIBELLE": "COMMUNE"}
        )
        comer["REG"], comer["REGION"], comer["TYPECOM"], comer["COMPARENT"] = pd.NA, "Collectivités d'outre-mer", "COMER", pd.NA

        history["DATE_DEBUT_SORT"] = pd.to_datetime(history["DATE_DEBUT"], errors="coerce")
        history = history.sort_values(["COM", "DATE_DEBUT_SORT"]).drop_duplicates("COM", keep="last")
        old = history[~history["COM"].isin(set(current["COM"]) | set(comer["COM"]))][["COM", "LIBELLE"]].rename(columns={"LIBELLE": "COMMUNE"})
        old["DEP"] = old["COM"].map(lambda code: code[:3] if code.startswith(("97", "98")) else code[:2])
        old["TYPECOM"], old["COMPARENT"] = "HIST", pd.NA

        current = current.merge(departments, on="DEP", how="left").merge(regions, on="REG", how="left")
        old = old.merge(departments_regions, on="DEP", how="left").merge(regions, on="REG", how="left")
        reference = pd.concat([current, comer[["COM", "DEP", "REG", "TYPECOM", "COMPARENT", "COMMUNE", "DEPARTEMENT", "REGION"]], old], ignore_index=True).drop_duplicates("COM")
        reference = reference.merge(populations, on="COM", how="left", validate="one_to_one")
        reference = reference.rename(columns={
            "COM": "code_commune", "COMMUNE": "commune", "TYPECOM": "type_commune",
            "COMPARENT": "code_commune_parente", "DEP": "code_departement", "DEPARTEMENT": "departement",
            "REG": "code_region", "REGION": "region", "PMUN": "population_municipale_2022",
            "PCAP": "population_comptee_a_part_2022", "PTOT": "population_totale_2022",
        })
        reference.to_csv(args.output, sep=";", index=False, encoding="utf-8-sig")
        print(f"OK {args.output} : {len(reference)} lignes")


if __name__ == "__main__":
    main()
