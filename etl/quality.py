"""Contrôles bloquants exécutés avant le chargement."""

from __future__ import annotations

from dataclasses import dataclass

from etl.transform import WarehouseFrames


@dataclass(frozen=True)
class QualitySummary:
    accidents: int
    unknown_dates: int
    unknown_times: int
    unknown_localities: int


def validate(frames: WarehouseFrames) -> QualitySummary:
    fact = frames.fact_accident
    errors: list[str] = []
    if fact["num_acc"].isna().any():
        errors.append("Num_Acc manquant")
    if fact["num_acc"].duplicated().any():
        errors.append("Num_Acc dupliqué")
    expected_victims = fact["nombre_tues"] + fact["nombre_blesses_hospitalises"] + fact["nombre_blesses_legers"]
    if not fact["nombre_victimes"].equals(expected_victims):
        errors.append("nombre_victimes incohérent")
    if (fact["nombre_usagers"] < fact["nombre_victimes"]).any():
        errors.append("nombre_usagers inférieur au nombre de victimes")
    expected_accidents = sum(count for name, count in frames.source_volumes.items() if name.startswith("caracteristiques_"))
    if len(fact) != expected_accidents:
        errors.append(f"volume des faits {len(fact)} différent des caractéristiques {expected_accidents}")
    if errors:
        raise ValueError("Contrôles qualité en échec: " + "; ".join(errors))
    known_localities = set(frames.dim_localisation["code_commune"].dropna())
    return QualitySummary(
        accidents=len(fact),
        unknown_dates=int((fact["date_key"] == 0).sum()),
        unknown_times=int((fact["horaire_key"] == 0).sum()),
        unknown_localities=int((~fact["code_commune"].isin(known_localities)).sum()),
    )
