# -*- coding: utf-8 -*-
"""Benchmark the Danish footprint against Eurostat's official FIGARO results.

Eurostat publishes consumption-based environmental footprints computed on the
FIGARO inter-country supply, use and input-output tables. Unlike EXIOBASE,
FIGARO's national blocks *are* the official national accounts, so its Danish
block is correct by construction. That makes it the natural independent check on
a study whose background model has just been shown to have a defective Danish
block in one release (see ``docs/methods/exiobase_release_and_classification.md``).

What Eurostat provides, and what it does not
--------------------------------------------
``env_ac_ghgfp`` gives greenhouse-gas footprints by destination country, origin
country, emitting NACE activity and final-demand category, annually to 2023.
This supports a national-total benchmark and a bilateral-origin comparison.

It does **not** support a health-sector benchmark directly: ``nace_r2`` is the
industry in which the emissions physically occur, not the purpose the final
demand serves. The closest available proxy is general-government final
consumption (``P3_S13``), of which Danish health care is a large but not
separable part.

``env_ac_rmefd`` (material footprints) *does* resolve final-use products
including ``CPA_Q86`` and ``CPA_Q87_88``, which is exactly this study's
boundary - but only for the EU27 aggregate, not for individual member states.
It is therefore usable as a per-capita sanity check, not as a Danish benchmark.

Notes
-----
The ``c_orig`` dimension mixes individual countries with aggregates
(``WORLD``, ``EU27_2020``, ``EXT_EU27_2020``, ``WRL_REST``). Summing the
dimension therefore double counts; ``WORLD`` is the total.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.figaro_benchmarks``
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Iterator

import pandas as pd

from analysis.constants import ANALYSIS_YEAR, DK_POPULATION
from analysis.build_figaro_dimensions import (aggregate_codes,
                                             code_labels)
from paths import OUTPUT_DIR

FOLDER = "06_benchmarks_validation"
API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

#: Published Danish national consumption-based GHG footprints, for benchmarking.
#:
#: The essential observation is that these split by MODEL FAMILY, not by year:
#: studies built on EXIOBASE land near 13 t per capita, while those coupling the
#: Danish national accounts to an MRIO land near 10-11. A result should be
#: judged against its own family before it is judged against the others.
PUBLISHED_BENCHMARKS: list[dict[str, Any]] = [
    dict(source="Eurostat FIGARO (env_ac_ghgfp)", year=2022,
         model_family="national accounts (FIGARO)", total_mt=57.4,
         per_capita_t=9.77, capital="exogenous",
         note="official EU statistical product"),
    dict(source="Statistics Denmark AFTRYK", year=2022,
         model_family="national accounts coupled to EXIOBASE", total_mt=62.9,
         per_capita_t=10.71, capital="exogenous",
         note="Denmark's official consumption-based account"),
    dict(source="Rørmose Jensen & Iliev 2022 (Statistics Denmark)", year=2020,
         model_family="national accounts coupled to EXIOBASE", total_mt=65.4,
         per_capita_t=11.0, capital="exogenous",
         note="simplified SNAC; 38 % arises in Denmark, 62 % abroad"),
    dict(source="Schmidt & Merciai 2023", year=2016,
         model_family="EXIOBASE (v4 hybrid)", total_mt=73.9, per_capita_t=12.9,
         capital="ENDOGENISED, contributing 1.1 t per capita",
         note="consequential/marginal model, so not a like-for-like "
              "attributional comparison, but the closest published Danish "
              "EXIOBASE-based figure"),
]

#: EU27 population, Eurostat ``demo_gind``, 1 January of the reference year.
EU27_POPULATION: dict[str, int] = {"2022": 446_735_291}


def fetch(dataset: str, **filters: str) -> dict[str, Any]:
    """Retrieve one Eurostat JSON-stat cube.

    Parameters
    ----------
    dataset : str
        Eurostat dataset code, for example ``"env_ac_ghgfp"``.
    **filters : str
        Dimension filters passed through as query parameters, for example
        ``time="2022"`` or ``c_dest="DK"``.

    Returns
    -------
    dict
        The parsed JSON-stat response.

    Raises
    ------
    RuntimeError
        If the request fails or the response is not valid JSON.
    """
    query = "&".join(f"{k}={v}" for k, v in filters.items())
    url = f"{API}/{dataset}?format=JSON&{query}"
    out = subprocess.run(["curl", "-s", "--max-time", "180", url],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"curl failed for {dataset}: {out.stderr[:200]}")
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{dataset}: non-JSON response ({exc})") from exc


def records(cube: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Flatten a JSON-stat cube into one record per observation.

    JSON-stat stores values against a single flat index into the cartesian
    product of the dimensions, in row-major order. This unravels that index.

    Parameters
    ----------
    cube : dict
        A parsed JSON-stat cube, as returned by :func:`fetch`.

    Yields
    ------
    dict
        One record per observation, with a key per dimension holding that
        dimension's category code, plus ``"value"``.
    """
    ids: list[str] = cube["id"]
    size: list[int] = cube["size"]
    codes = {k: list(cube["dimension"][k]["category"]["index"].keys())
             for k in ids}
    for flat, value in cube["value"].items():
        rest, position = int(flat), []
        for extent in reversed(size):
            position.append(rest % extent)
            rest //= extent
        position.reverse()
        rec = {name: codes[name][p] for name, p in zip(ids, position)}
        rec["value"] = value
        yield rec


def _our_results() -> dict[str, Any]:
    """Read this study's own headline totals, and their label, from gold.

    The label comes out of the file with the numbers, never from
    :data:`constants.MODEL_LABEL`. ``MODEL_LABEL`` describes the background the
    *current process* would load, and this function loads no background at all:
    it reads CSVs that some earlier run wrote. Those two disagree whenever this
    module runs in a different environment from the run that produced the gold
    tables, and the disagreement is silent and in the worst direction -- with no
    ``HC_BACKGROUND_TAG`` set, corrected numbers get stamped
    ``EXIOBASE v3.8.2 IOT_2022_ixi``, asserting in a published benchmark table
    that the Danish sea-transport reallocation was not applied when it was.

    Returns
    -------
    dict
        ``"healthcare_climate_kt"``, ``"national_climate_kt"`` and
        ``"healthcare_share_pct"`` as floats, and ``"model"``, the provenance
        string the gold table carries.

    Raises
    ------
    RuntimeError
        If the summary lacks the climate row, the ``national_footprint`` column
        or the ``model`` column that carries the provenance.
    """
    core = os.path.join(str(OUTPUT_DIR), "00_core_footprint")
    hc = pd.read_csv(os.path.join(core, "footprint_by_producing_node.csv"))
    nat = pd.read_csv(os.path.join(core, "national_totals_summary.csv"))
    out: dict[str, Any] = {
        "healthcare_climate_kt":
        float(hc.loc[hc.indicator == "climate_change", "value"].sum())}
    row = nat[nat.indicator == "climate_change"]
    missing = [c for c in ("national_footprint", "model")
               if c not in nat.columns]
    if row.empty or missing:
        raise RuntimeError(
            "national_totals_summary.csv lacks a climate_change row or the "
            f"column(s) {missing}; run analysis.national_totals first")
    out["national_climate_kt"] = float(row["national_footprint"].iloc[0])
    out["healthcare_share_pct"] = float(row["healthcare_share_pct"].iloc[0])
    out["model"] = str(row["model"].iloc[0])
    return out


def main() -> None:
    """Build the FIGARO benchmark tables and write them to the gold folder."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    year = ANALYSIS_YEAR

    # ---- Danish national footprint, by final-demand category ------------
    cube = fetch("env_ac_ghgfp", time=year, c_dest="DK", c_orig="WORLD",
                 nace_r2="TOTAL")
    labels = cube["dimension"]["na_item"]["category"]["label"]
    demand = [dict(country_consuming="DNK", final_demand_category=r["na_item"],
                   final_demand_label=labels[r["na_item"]],
                   value=r["value"], unit="kt CO2eq",
                   source=f"Eurostat env_ac_ghgfp (FIGARO), {year}")
              for r in records(cube)]
    demand_df = pd.DataFrame(demand).sort_values("final_demand_category")
    demand_df.to_csv(
        os.path.join(out_dir, "figaro_dk_footprint_by_final_demand.csv"),
        index=False)

    # ---- bilateral origin structure -------------------------------------
    cube = fetch("env_ac_ghgfp", time=year, c_dest="DK", na_item="TOTAL",
                 nace_r2="TOTAL")
    # The aggregate set is read from the silver dimension table rather than
    # written here, because the four codes it used to hold were not four of a
    # kind: WORLD, EU27_2020 and EXT_EU27_2020 each overlap their members and
    # must come out of a sum, while WRL_REST is the residual for the countries
    # FIGARO does not resolve and must stay in. Flagging the residual as an
    # aggregate invites a consumer of this file to drop the rest of the world.
    aggregates = aggregate_codes("c_orig")
    origin_labels = code_labels("c_orig")
    origin = [dict(country_consuming="DNK", country_producing=r["c_orig"],
                   country_producing_label=origin_labels.get(r["c_orig"], ""),
                   is_aggregate=r["c_orig"] in aggregates,
                   value=r["value"], unit="kt CO2eq",
                   source=f"Eurostat env_ac_ghgfp (FIGARO), {year}")
              for r in records(cube)]
    origin_df = pd.DataFrame(origin).sort_values("value", ascending=False)
    origin_df.to_csv(
        os.path.join(out_dir, "figaro_dk_footprint_by_origin.csv"), index=False)

    figaro_total = float(
        demand_df.loc[demand_df.final_demand_category == "TOTAL",
                      "value"].iloc[0])
    figaro_government = float(
        demand_df.loc[demand_df.final_demand_category == "P3_S13",
                      "value"].iloc[0])

    # ---- EU27 material footprint of health, per capita ------------------
    material: list[dict[str, Any]] = []
    for cpa, label in (("CPA_Q86", "Human health services"),
                       ("CPA_Q87_88", "Residential care and social work")):
        cube = fetch("env_ac_rmefd", time=year, unit="THS_T", material="TOTAL",
                     indic_env="RMC", cpa08=cpa)
        for r in records(cube):
            material.append(dict(
                country_consuming=r["geo"], sector_consuming=label,
                cpa_code=cpa, value=r["value"], unit="kt",
                per_capita_t=r["value"] * 1e3 / EU27_POPULATION[year]
                if r["geo"] == "EU27_2020" and year in EU27_POPULATION
                else float("nan"),
                source=f"Eurostat env_ac_rmefd (FIGARO), {year}",
                note="EU27 aggregate only; Eurostat publishes no member-state "
                     "detail for this dataset"))
    material_df = pd.DataFrame(material)
    material_df.to_csv(
        os.path.join(out_dir, "figaro_eu27_material_footprint_health.csv"),
        index=False)

    # ---- the comparison itself ------------------------------------------
    ours = _our_results()
    pop = DK_POPULATION[year]
    comparison = pd.DataFrame([
        dict(quantity="Danish national consumption-based GHG footprint",
             source="Eurostat FIGARO (env_ac_ghgfp)", value=figaro_total,
             unit="kt CO2eq", per_capita_t=figaro_total * 1e3 / pop),
        dict(quantity="Danish national consumption-based GHG footprint",
             source="Statistics Denmark AFTRYK", value=62_900.0,
             unit="kt CO2eq", per_capita_t=62_900.0 * 1e3 / pop),
        dict(quantity="Danish national consumption-based GHG footprint",
             source=f"this study ({ours['model']})",
             value=ours["national_climate_kt"], unit="kt CO2eq",
             per_capita_t=ours["national_climate_kt"] * 1e3 / pop),
        dict(quantity="Danish general-government final consumption footprint",
             source="Eurostat FIGARO (env_ac_ghgfp, P3_S13)",
             value=figaro_government, unit="kt CO2eq",
             per_capita_t=figaro_government * 1e3 / pop),
        dict(quantity="Danish health-care footprint, MRIO component",
             source=f"this study ({ours['model']})",
             value=ours["healthcare_climate_kt"], unit="kt CO2eq",
             per_capita_t=ours["healthcare_climate_kt"] * 1e3 / pop),
    ])
    comparison["ratio_to_figaro_national"] = (
        comparison["value"] / figaro_total)

    published = pd.DataFrame(PUBLISHED_BENCHMARKS)
    published.loc[len(published)] = dict(
        source=f"this study ({ours['model']})", year=int(year),
        model_family="EXIOBASE (v3.8.2, sea-transport reallocation)",
        total_mt=ours["national_climate_kt"] / 1e3,
        per_capita_t=ours["national_climate_kt"] * 1e3 / pop,
        capital="exogenous (excluded from the headline)",
        note="attributional")
    published = published.sort_values("per_capita_t")
    published.to_csv(
        os.path.join(out_dir, "published_danish_footprint_benchmarks.csv"),
        index=False)
    comparison.insert(0, "analysis_year", year)
    comparison.to_csv(
        os.path.join(out_dir, "figaro_vs_this_study_climate.csv"), index=False)

    pd.set_option("display.width", 200)
    print(f"FIGARO Danish national GHG footprint {year}: "
          f"{figaro_total:,.0f} kt CO2eq")
    print(demand_df[["final_demand_category", "value",
                     "final_demand_label"]].to_string(index=False))
    print()
    print(comparison[["quantity", "source", "value",
                      "per_capita_t"]].to_string(index=False))
    print("\nPublished Danish national footprints, by model family:")
    print(published[["source", "year", "model_family", "per_capita_t"]]
          .to_string(index=False, max_colwidth=46))
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
