"""Télécharge les quatre fichiers BAAC nécessaires pour chaque millésime."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

API_URL = "https://www.data.gouv.fr/api/1/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/"
KINDS = {
    "caracteristiques": ("caract", "caracteristiques", "carcteristiques"),
    "lieux": ("lieux",),
    "vehicules": ("vehicules",),
    "usagers": ("usagers",),
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_catalog() -> dict:
    request = urllib.request.Request(API_URL, headers={"User-Agent": "baac-datawarehouse-school-project/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def select_resource(resources: list[dict], kind: str, year: int) -> dict:
    prefixes = KINDS[kind]
    candidates = []
    for resource in resources:
        name = normalize(" ".join(str(resource.get(key, "")) for key in ("title", "url")))
        if str(year) in name and any(prefix in name for prefix in prefixes) and resource.get("url"):
            candidates.append(resource)
    if not candidates:
        raise RuntimeError(f"Ressource introuvable : {kind} {year}")
    candidates.sort(key=lambda item: str(item.get("last_modified", "")), reverse=True)
    return candidates[0]


def download(url: str, target: Path, overwrite: bool) -> None:
    if target.exists() and not overwrite:
        print(f"SKIP {target.name}")
        return
    request = urllib.request.Request(url, headers={"User-Agent": "baac-datawarehouse-school-project/1.0"})
    temporary = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(request, timeout=180) as response, temporary.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    temporary.replace(target)
    print(f"OK   {target.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-year", type=int, default=2019)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--output", type=Path, default=Path("data/raw/baac"))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    resources = load_catalog()["resources"]
    manifest = []
    for year in range(args.start_year, args.end_year + 1):
        for kind in KINDS:
            resource = select_resource(resources, kind, year)
            target = args.output / f"{kind}-{year}.csv"
            download(resource["url"], target, args.overwrite)
            manifest.append({
                "file": target.name,
                "source_url": resource["url"],
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                "bytes": target.stat().st_size,
            })
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK   manifest.json ({len(manifest)} fichiers)")


if __name__ == "__main__":
    main()
