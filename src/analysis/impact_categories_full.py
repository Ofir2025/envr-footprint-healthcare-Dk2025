# -*- coding: utf-8 -*-
"""Full impact-category profile for Danish health care, all DESIRE methods.

Why this module exists
----------------------
The study's own headline uses six indicators. The studies it is benchmarked
against use different and wider sets: Eckelman & Sherman (2016) report nine
TRACI categories plus DALYs, Malik et al. (2021) report several environmental
impacts, and Lenzen et al. (2020) report a long KPI list. Comparing on one
stressor at a time is not a replication.

The characterisation workbook shipped with the background
(``characterisation_desire_version3_4_adapted.xlsx``) already contains **121
emission categories** across CML 1999, USEtox, EcoIndicator 99 and the ILCD
recommended factors, plus resource and material categories. The pipeline only
ever used six of them. This module computes them all, once, so that every
study-replication layer can select the subset it needs from a single consistent
calculation rather than each rebuilding its own characterisation.

Crucially, the ILCD block includes **endpoint factors in DALYs** for climate
change, ozone depletion, human toxicity (cancer and non-cancer), particulate
matter, photochemical ozone formation and ionising radiation. That allows the
Eckelman DALY column to be reproduced for Denmark with one internally
consistent method, instead of his mixture of TRACI 1 characterisation, TRACI 2.1
normalisation and IMPACT 2002+ damage factors.

Scope of the numbers produced here
----------------------------------
These are the **supply-chain (MRIO) components only**. The Danish direct
operational component is primary national data (DRIVHUS emissions, AFFALD01
waste) and has no full stressor profile, so it can be added for climate and
waste but not for the other categories. Every row states this in its
``component`` field rather than leaving it to be inferred.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.impact_categories_full``
"""

from __future__ import annotations

import os
import pickle
from typing import Any

import numpy as np
import pandas as pd

from analysis.constants import (ANALYSIS_YEAR, BACKGROUND_YEAR, DK_POPULATION,
                                K_DK, MODEL_LABEL, N_FINAL_DEMAND)
from paths import BACKGROUND_DIR, EXIOBASE_DIR, MRIO_DIR, OUTPUT_DIR

FOLDER = "12_impact_categories_full"
CHAR_WORKBOOK = "characterisation_desire_version3_4_adapted.xlsx"

#: Offsets of each satellite domain within the 1113-row stressor vector.
#: Taken from ``pipelines.prep_background_2025.load``, which builds the
#: six-row production version of this same matrix.
DOMAIN_OFFSET: dict[str, int] = {
    "Q_factorinputs": 0,
    "Q_emissions": 23,
    "Q_resources": 446,
    "Q_materials": 466,
}

#: Number of index levels each characterisation sheet uses, and which level
#: carries the category name and the unit.
SHEET_INDEX: dict[str, tuple[list[int], int, int]] = {
    "Q_factorinputs": ([0, 1], 0, 1),
    "Q_emissions": ([0, 1, 2, 3], 1, 3),
    "Q_resources": ([0, 1], 0, 1),
    "Q_materials": ([0, 1], 0, 1),
}


def build_full_characterisation(n_stressors: int) -> tuple[np.ndarray,
                                                           pd.DataFrame]:
    """Assemble every DESIRE impact category into one characterisation matrix.

    Parameters
    ----------
    n_stressors : int
        Length of the stressor vector the matrix must span (1113 for
        EXIOBASE v3.8.2 plus the appended waste row).

    Returns
    -------
    Q : numpy.ndarray, shape (n_categories, n_stressors)
        Characterisation factors, one row per impact category.
    meta : pandas.DataFrame
        One row per category with ``method``, ``indicator``, ``unit``,
        ``sheet`` and ``n_nonzero_factors``.

    Notes
    -----
    A category is kept only if it has at least one non-zero factor that lands
    inside the stressor vector; categories whose factors all fall outside are
    reported in ``meta`` with ``n_nonzero_factors == 0`` and produce zero, so a
    silent zero can always be distinguished from a genuine one.
    """
    path = os.path.join(str(EXIOBASE_DIR), CHAR_WORKBOOK)
    rows: list[np.ndarray] = []
    meta: list[dict[str, Any]] = []
    for sheet, (index_cols, name_level, unit_level) in SHEET_INDEX.items():
        frame = pd.read_excel(path, sheet_name=sheet, index_col=index_cols,
                              header=[0, 1])
        offset = DOMAIN_OFFSET[sheet]
        values = np.nan_to_num(np.asarray(frame, dtype=float))
        for position in range(frame.shape[0]):
            factors = values[position]
            nonzero = np.flatnonzero(factors)
            columns = nonzero + offset
            inside = columns < n_stressors
            row = np.zeros(n_stressors)
            row[columns[inside]] = factors[nonzero[inside]]
            label = frame.index[position]
            method = str(label[0])
            name = str(label[name_level])
            unit = str(label[unit_level])
            if name.lower() in ("nan", "") or method.lower() == "nan":
                continue
            rows.append(row)
            meta.append(dict(method=method, indicator=name, unit=unit,
                             sheet=sheet,
                             n_nonzero_factors=int(inside.sum())))
    return np.vstack(rows), pd.DataFrame(meta)


def _screen(table: pd.DataFrame) -> pd.Series:
    """Flag characterisation rows that cannot be taken at face value.

    Two failure modes are screened for, both observed in the shipped DESIRE
    workbook:

    ``DUPLICATE_OF_MIDPOINT``
        An endpoint row whose computed value is bit-identical to its midpoint
        row while carrying a different unit. The endpoint factors are then a
        copy of the midpoint factors and the row carries no damage information.

    ``ENDPOINT_MIDPOINT_RATIO_IMPLAUSIBLE``
        An endpoint/midpoint ratio more than two orders of magnitude away from
        the corresponding published damage factor. Retained for transparency,
        but must not be reported as a damage estimate without checking the
        underlying factors.

    Parameters
    ----------
    table : pandas.DataFrame
        The assembled result table, before writing.

    Returns
    -------
    pandas.Series
        One flag string per row; ``"ok"`` where no problem was detected.
    """
    flags = pd.Series("ok", index=table.index, dtype=object)
    values = table["healthcare_supply_chain"]
    for i, row in table.iterrows():
        name = str(row["indicator"])
        if "endpoint" not in name.lower():
            continue
        stem = name.lower().split("endpoint")[0].strip(" ,")
        peers = table[(table.index != i)
                      & table.indicator.str.lower().str.startswith(stem)
                      & table.indicator.str.contains("midpoint", case=False)]
        if peers.empty:
            continue
        midpoint = float(peers["healthcare_supply_chain"].iloc[0])
        endpoint = float(values.iloc[i])
        if midpoint != 0 and endpoint == midpoint \
                and row["unit"] != peers["unit"].iloc[0]:
            flags.iloc[i] = "DUPLICATE_OF_MIDPOINT"
        elif midpoint != 0 and row["unit"].strip().upper() == "DALY" \
                and abs(endpoint / midpoint) < 1e-7:
            flags.iloc[i] = "ENDPOINT_MIDPOINT_RATIO_IMPLAUSIBLE"
    return flags


def main() -> None:
    """Compute and write the full impact profile for Denmark."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(str(MRIO_DIR),
                           f"mrio{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        mrio = pickle.load(fh)
    with open(os.path.join(str(MRIO_DIR),
                           f"leontief{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        leontief = pickle.load(fh)
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"),
              "rb") as fh:
        background = pickle.load(fh)

    raw_stressors: np.ndarray = mrio["R"]
    output: np.ndarray = mrio["x"][:, 0]
    demand_all: np.ndarray = mrio["Y"]
    demand_health: np.ndarray = background["Ystim"][:, 0]

    Q, meta = build_full_characterisation(raw_stressors.shape[0])
    print(f"characterisation: {Q.shape[0]} categories over "
          f"{Q.shape[1]} stressors")

    inverse_output = np.divide(1.0, output, out=np.zeros_like(output),
                               where=output > 0)
    intensities = raw_stressors * inverse_output[np.newaxis, :]

    danish_final_demand = demand_all[
        :, K_DK * N_FINAL_DEMAND:(K_DK + 1) * N_FINAL_DEMAND].sum(axis=1)

    stressors_health = intensities @ (leontief @ demand_health)
    stressors_nation = intensities @ (leontief @ danish_final_demand)

    impacts_health = Q @ stressors_health
    impacts_nation = Q @ stressors_nation

    population = DK_POPULATION[ANALYSIS_YEAR]
    table = meta.copy()
    table.insert(0, "country_consuming", "DNK")
    table.insert(1, "analysis_year", ANALYSIS_YEAR)
    table["healthcare_supply_chain"] = impacts_health
    table["national_supply_chain"] = impacts_nation
    with np.errstate(divide="ignore", invalid="ignore"):
        share = np.where(impacts_nation != 0,
                         100.0 * impacts_health / impacts_nation, np.nan)
    table["healthcare_share_of_national_pct"] = share
    table["healthcare_per_capita"] = impacts_health / population
    table["component"] = ("supply chain (MRIO) only; the Danish direct "
                          "operational component is national primary data and "
                          "has a full stressor profile only for climate and "
                          "waste")
    table["model"] = MODEL_LABEL
    table["sector_consuming"] = "health_and_eldercare"
    table = table[table.n_nonzero_factors > 0].reset_index(drop=True)
    table["quality_flag"] = _screen(table)
    table.to_csv(os.path.join(out_dir, "impact_categories_all_methods.csv"),
                 index=False)

    stressor_labels = list(mrio["label"]["extension"].iloc[:, 0]) \
        if "extension" in mrio["label"] else \
        [f"stressor_{i}" for i in range(raw_stressors.shape[0])]
    stressor_table = pd.DataFrame(dict(
        country_consuming="DNK", sector_consuming="health_and_eldercare",
        analysis_year=ANALYSIS_YEAR, stressor=stressor_labels[:len(stressors_health)],
        healthcare_supply_chain=stressors_health,
        national_supply_chain=stressors_nation, model=MODEL_LABEL))
    stressor_table = stressor_table[stressor_table.healthcare_supply_chain != 0]
    stressor_table.to_csv(
        os.path.join(out_dir, "stressor_totals_uncharacterised.csv"),
        index=False)

    pd.set_option("display.width", 210)
    ilcd = table[table.method.str.contains("ILCD", na=False)]
    print(f"\n{len(table)} categories computed; ILCD block "
          f"({len(ilcd)} categories), Danish health care:")
    print(ilcd[["indicator", "unit", "healthcare_supply_chain",
                "healthcare_share_of_national_pct", "quality_flag"]]
          .to_string(index=False, max_colwidth=48))
    flagged = table[table.quality_flag != "ok"]
    if not flagged.empty:
        print(f"\n{len(flagged)} categories flagged as untrustworthy:")
        print(flagged[["method", "indicator", "unit", "quality_flag"]]
              .to_string(index=False, max_colwidth=44))
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
