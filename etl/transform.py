"""Règles de transformation métier du Data Warehouse BAAC."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

import pandas as pd

UNKNOWN = "Non renseigné"

LUMINOSITE = {1: "Plein jour", 2: "Crépuscule ou aube", 3: "Nuit sans éclairage public", 4: "Nuit avec éclairage public non allumé", 5: "Nuit avec éclairage public allumé"}
TYPE_ZONE = {1: "Hors agglomération", 2: "En agglomération"}
INTERSECTION = {1: "Hors intersection", 2: "Intersection en X", 3: "Intersection en T", 4: "Intersection en Y", 5: "Intersection à plus de quatre branches", 6: "Giratoire", 7: "Place", 8: "Passage à niveau", 9: "Autre intersection"}
METEO = {1: "Normale", 2: "Pluie légère", 3: "Pluie forte", 4: "Neige ou grêle", 5: "Brouillard ou fumée", 6: "Vent fort ou tempête", 7: "Temps éblouissant", 8: "Temps couvert", 9: "Autre"}
COLLISION = {1: "Deux véhicules - frontale", 2: "Deux véhicules - par l'arrière", 3: "Deux véhicules - par le côté", 4: "Trois véhicules et plus - en chaîne", 5: "Trois véhicules et plus - collisions multiples", 6: "Autre collision", 7: "Sans collision"}
CATEGORIE_ROUTE = {1: "Autoroute", 2: "Route nationale", 3: "Route départementale", 4: "Voie communale", 5: "Hors réseau public", 6: "Parc de stationnement ouvert", 7: "Route de métropole urbaine", 9: "Autre"}
CIRCULATION = {1: "Sens unique", 2: "Bidirectionnelle", 3: "Chaussées séparées", 4: "Voies à affectation variable"}
VOIE_RESERVEE = {0: "Aucune", 1: "Piste cyclable", 2: "Bande cyclable", 3: "Voie réservée"}
PROFIL = {1: "Plat", 2: "Pente", 3: "Sommet de côte", 4: "Bas de côte"}
TRACE = {1: "Partie rectiligne", 2: "Courbe à gauche", 3: "Courbe à droite", 4: "Courbe en S"}
SURFACE = {1: "Normale", 2: "Mouillée", 3: "Flaques", 4: "Inondée", 5: "Enneigée", 6: "Boue", 7: "Verglacée", 8: "Corps gras ou huile", 9: "Autre"}
INFRASTRUCTURE = {0: "Aucune", 1: "Souterrain ou tunnel", 2: "Pont ou autopont", 3: "Bretelle d'échangeur", 4: "Voie ferrée", 5: "Carrefour aménagé", 6: "Zone piétonne", 7: "Zone de péage", 8: "Chantier", 9: "Autre"}
SITUATION = {1: "Sur chaussée", 2: "Bande d'arrêt d'urgence", 3: "Accotement", 4: "Trottoir", 5: "Piste cyclable", 6: "Autre voie spéciale", 8: "Autre"}


@dataclass
class WarehouseFrames:
    dim_date: pd.DataFrame
    dim_horaire: pd.DataFrame
    dim_localisation: pd.DataFrame
    dim_route: pd.DataFrame
    dim_circonstance: pd.DataFrame
    fact_accident: pd.DataFrame
    source_volumes: dict[str, int]


def clean_text(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.replace("\u00a0", "", regex=False).str.strip()
    return cleaned.replace({"": pd.NA, "N/A": pd.NA, "NA": pd.NA, "-1": pd.NA})


def integer(series: pd.Series) -> pd.Series:
    return pd.to_numeric(clean_text(series), errors="coerce").astype("Int64")


def decimal(series: pd.Series) -> pd.Series:
    return pd.to_numeric(clean_text(series).str.replace(",", ".", regex=False), errors="coerce")


def label(code: pd.Series, mapping: dict[int, str]) -> pd.Series:
    return integer(code).map(mapping).fillna(UNKNOWN)


def stable_hash(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    def digest(row: pd.Series) -> str:
        payload = [None if pd.isna(row[column]) else str(row[column]) for column in columns]
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False).encode("utf-8")).hexdigest()
    return frame.apply(digest, axis=1)


def normalize_commune(series: pd.Series) -> pd.Series:
    def one(value: object) -> object:
        if pd.isna(value):
            return pd.NA
        text = re.sub(r"\s+", "", str(value)).upper()
        return text.zfill(5) if text.isdigit() and len(text) < 5 else text
    return clean_text(series).map(one)


def build_date_dimension(start_year: int, end_year: int) -> pd.DataFrame:
    dates = pd.date_range(f"{start_year}-01-01", f"{end_year}-12-31", freq="D")
    months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    iso = dates.isocalendar()
    return pd.DataFrame({"date_key": dates.strftime("%Y%m%d").astype(int), "full_date": dates.date, "annee": dates.year, "trimestre": dates.quarter, "mois": dates.month, "mois_nom": [months[value - 1] for value in dates.month], "annee_mois": dates.strftime("%Y-%m"), "semaine_iso": iso.week.astype(int), "jour": dates.day, "jour_semaine_iso": dates.dayofweek + 1, "jour_nom": [days[value] for value in dates.dayofweek], "est_weekend": dates.dayofweek >= 5})


def build_time_dimension() -> pd.DataFrame:
    minute_of_day = pd.Series(range(1440), name="minute_of_day")
    hours, minutes = minute_of_day // 60, minute_of_day % 60
    period = pd.cut(hours, bins=[-1, 5, 11, 17, 23], labels=["Nuit", "Matin", "Après-midi", "Soir"])
    return pd.DataFrame({"horaire_key": minute_of_day + 1, "heure": hours, "minute": minutes, "heure_libelle": [f"{hour:02d}:{minute:02d}" for hour, minute in zip(hours, minutes)], "tranche_horaire": [f"{hour:02d}:00-{hour:02d}:59" for hour in hours], "periode_journee": period.astype("string")})


def transform_insee(source: pd.DataFrame) -> pd.DataFrame:
    columns = ["code_commune", "type_commune", "code_commune_parente", "commune", "code_departement", "departement", "code_region", "region", "population_municipale_2022", "population_comptee_a_part_2022", "population_totale_2022"]
    result = source.reindex(columns=columns).copy()
    result["code_commune"] = normalize_commune(result["code_commune"])
    numeric = {"population_municipale_2022", "population_comptee_a_part_2022", "population_totale_2022"}
    for column in numeric:
        result[column] = integer(result[column])
    result["code_commune_parente"] = normalize_commune(result["code_commune_parente"])
    result["code_region"] = clean_text(result["code_region"])
    result["code_departement"] = clean_text(result["code_departement"]).fillna("N/C")
    for column in ("type_commune", "commune", "departement", "region"):
        result[column] = clean_text(result[column]).fillna(UNKNOWN)
    return result.dropna(subset=["code_commune"]).drop_duplicates("code_commune")


def transform_year(sources: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    car, lieux, veh, usa = (sources[name].copy() for name in ("caracteristiques", "lieux", "vehicules", "usagers"))
    for frame in (car, lieux, veh, usa):
        frame["num_acc"] = clean_text(frame["num_acc"])

    for column in ("jour", "mois", "an", "lum", "agg", "int", "atm", "col"):
        car[column] = integer(car[column])
    car["event_date"] = pd.to_datetime(dict(year=car["an"], month=car["mois"], day=car["jour"]), errors="coerce")
    parts = clean_text(car["hrmn"]).str.extract(r"^(\d{1,2})[:hH]?(\d{2})$")
    car["heure"], car["minute"] = pd.to_numeric(parts[0], errors="coerce"), pd.to_numeric(parts[1], errors="coerce")
    valid_time = car["heure"].between(0, 23) & car["minute"].between(0, 59)
    car["horaire_key"] = ((car["heure"] * 60 + car["minute"] + 1).where(valid_time, 0)).astype(int)
    car["date_key"] = pd.to_numeric(car["event_date"].dt.strftime("%Y%m%d"), errors="coerce").fillna(0).astype(int)
    car["code_commune"] = normalize_commune(car["com"])
    car["latitude"], car["longitude"], car["adresse"] = decimal(car["lat"]), decimal(car["long"]), clean_text(car["adr"])
    for code, raw, labels, name in [("luminosite_code", "lum", LUMINOSITE, "luminosite"), ("type_zone_code", "agg", TYPE_ZONE, "type_zone"), ("intersection_code", "int", INTERSECTION, "intersection"), ("meteo_code", "atm", METEO, "meteo"), ("collision_code", "col", COLLISION, "type_collision")]:
        car[code], car[name] = car[raw], label(car[raw], labels)
    circumstance_codes = ["luminosite_code", "type_zone_code", "intersection_code", "meteo_code", "collision_code"]
    car["circonstance_profile_code"] = stable_hash(car, circumstance_codes)

    route_raw = ["catr", "circ", "nbv", "vosp", "prof", "plan", "surf", "infra", "situ", "vma"]
    for column in route_raw:
        lieux[column] = integer(lieux[column])
    lieux["voie"] = clean_text(lieux["voie"])
    lieux["route_priority"] = lieux["catr"].map({1: 1, 2: 2, 3: 3, 7: 4, 4: 5}).fillna(9)
    lieux["named_priority"] = lieux["voie"].isna().astype(int)
    place_count = lieux.groupby("num_acc", dropna=False).size().rename("nombre_lieux_associes")
    main_place = lieux.sort_values(["num_acc", "route_priority", "named_priority", "source_row_number"]).drop_duplicates("num_acc").copy()
    route_labels = [("categorie_route_code", "catr", CATEGORIE_ROUTE, "categorie_route"), ("circulation_code", "circ", CIRCULATION, "circulation"), ("voie_reservee_code", "vosp", VOIE_RESERVEE, "voie_reservee"), ("profil_code", "prof", PROFIL, "profil"), ("trace_code", "plan", TRACE, "trace"), ("surface_code", "surf", SURFACE, "etat_surface"), ("infrastructure_code", "infra", INFRASTRUCTURE, "infrastructure"), ("situation_code", "situ", SITUATION, "situation")]
    for code, raw, labels, name in route_labels:
        main_place[code], main_place[name] = main_place[raw], label(main_place[raw], labels)
    main_place["tranche_vitesse"] = pd.cut(main_place["vma"], bins=[-1, 30, 50, 70, 90, 110, 999], labels=["0-30", "31-50", "51-70", "71-90", "91-110", ">110"]).astype("string").fillna(UNKNOWN)
    main_place["route_profile_code"] = stable_hash(main_place, route_raw)
    main_place = main_place.merge(place_count, on="num_acc", how="left")

    usa["grav"], usa["catu"] = integer(usa["grav"]), integer(usa["catu"])
    flags = {"nombre_indemnes": usa["grav"] == 1, "nombre_tues": usa["grav"] == 2, "nombre_blesses_hospitalises": usa["grav"] == 3, "nombre_blesses_legers": usa["grav"] == 4, "nombre_conducteurs": usa["catu"] == 1, "nombre_passagers": usa["catu"] == 2, "nombre_pietons": usa["catu"] == 3}
    for name, values in flags.items():
        usa[name] = values.fillna(False).astype(int)
    user_agg = usa.groupby("num_acc").agg(nombre_usagers=("num_acc", "size"), **{name: (name, "sum") for name in flags}).reset_index()
    user_agg["nombre_victimes"] = user_agg["nombre_tues"] + user_agg["nombre_blesses_hospitalises"] + user_agg["nombre_blesses_legers"]

    veh["catv"] = integer(veh["catv"])
    veh["vehicle_identifier"] = clean_text(veh.get("id_vehicule", veh["num_veh"])).fillna(clean_text(veh["num_veh"]))
    two_wheels = set(range(1, 7)) | set(range(30, 35)) | set(range(40, 44)) | {50, 60, 80}
    for name, values in {"is_light": veh["catv"].isin({7, 10}), "is_two_wheels": veh["catv"].isin(two_wheels), "is_heavy": veh["catv"].isin({13, 14, 15, 16, 17, 20, 21, 37, 38, 39})}.items():
        veh[name] = values.astype(int)
    vehicle_agg = veh.groupby("num_acc").agg(nombre_vehicules=("vehicle_identifier", "nunique"), nombre_vehicules_legers=("is_light", "sum"), nombre_deux_roues=("is_two_wheels", "sum"), nombre_poids_lourds=("is_heavy", "sum")).reset_index()

    circumstance_output = ["circonstance_profile_code", "luminosite_code", "luminosite", "type_zone_code", "type_zone", "intersection_code", "intersection", "meteo_code", "meteo", "collision_code", "type_collision"]
    route_output = ["route_profile_code", "categorie_route_code", "categorie_route", "circulation_code", "circulation", "nbv", "voie_reservee_code", "voie_reservee", "profil_code", "profil", "trace_code", "trace", "surface_code", "etat_surface", "infrastructure_code", "infrastructure", "situation_code", "situation", "vma", "tranche_vitesse"]
    base = car[["num_acc", "date_key", "horaire_key", "code_commune", "adresse", "latitude", "longitude", "source_year"] + circumstance_output]
    fact = base.merge(main_place[["num_acc", "voie", "nombre_lieux_associes"] + route_output], on="num_acc", how="left").merge(user_agg, on="num_acc", how="left").merge(vehicle_agg, on="num_acc", how="left")
    measures = ["nombre_lieux_associes", "nombre_usagers", "nombre_indemnes", "nombre_tues", "nombre_blesses_hospitalises", "nombre_blesses_legers", "nombre_victimes", "nombre_conducteurs", "nombre_passagers", "nombre_pietons", "nombre_vehicules", "nombre_vehicules_legers", "nombre_deux_roues", "nombre_poids_lourds"]
    fact[measures] = fact[measures].fillna(0).astype(int)
    fact["nombre_lieux_associes"] = fact["nombre_lieux_associes"].clip(lower=1)
    fact["est_multi_voies"], fact["est_accident_mortel"], fact["accident_count"] = fact["nombre_lieux_associes"] > 1, fact["nombre_tues"] > 0, 1
    fact = fact.rename(columns={"voie": "voie_principale", "source_year": "millesime_source"})
    route_dimension = main_place.rename(columns={"nbv": "nombre_voies", "vma": "vitesse_maximale"})[[column.replace("nbv", "nombre_voies").replace("vma", "vitesse_maximale") for column in route_output]].drop_duplicates("route_profile_code")
    circumstance_dimension = car[circumstance_output].drop_duplicates("circonstance_profile_code")
    return fact, route_dimension, circumstance_dimension


def combine(yearly_sources: list[dict[str, pd.DataFrame]], insee: pd.DataFrame, start_year: int, end_year: int) -> WarehouseFrames:
    facts, routes, circumstances, volumes = [], [], [], {}
    for sources in yearly_sources:
        year = int(sources["caracteristiques"]["source_year"].iloc[0])
        volumes.update({f"{name}_{year}": len(frame) for name, frame in sources.items()})
        fact, route, circumstance = transform_year(sources)
        facts.append(fact); routes.append(route); circumstances.append(circumstance)
    fact_all = pd.concat(facts, ignore_index=True)
    if fact_all["num_acc"].duplicated().any():
        examples = fact_all.loc[fact_all["num_acc"].duplicated(), "num_acc"].head().tolist()
        raise ValueError(f"Num_Acc dupliqué après transformation: {examples}")
    return WarehouseFrames(build_date_dimension(start_year, end_year), build_time_dimension(), transform_insee(insee), pd.concat(routes, ignore_index=True).drop_duplicates("route_profile_code"), pd.concat(circumstances, ignore_index=True).drop_duplicates("circonstance_profile_code"), fact_all, volumes)
