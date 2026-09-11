# -*- coding: utf-8 -*-
"""Three-way validation of the Danish health input recipe.

The healthcare-services footprint rests entirely on the input structure of the
Danish health industry. Until now that structure could be checked against one
alternative (the DST 117-industry IO table). Eurostat FIGARO supplies a third,
official, EU-harmonised view: its use table separates Q86 human health from
Q87_88 residential care and social work, giving the Danish health industry's
purchases by product and by country of origin.

Comparing all three answers two questions at once:
  * does the modelled Danish health recipe resemble the observed one?
  * do two independent official sources (DST national accounts and Eurostat
    FIGARO) agree with each other, i.e. is the benchmark itself trustworthy?

The modelled column is read at ``analysis.constants.BACKGROUND_YEAR`` and is
headed by ``analysis.constants.MODEL_LABEL``, so it names the release and the
variant it is: on the sea-transport-reallocated background the water transport
row is the residual left after the correction (0.6 %, against 3.9 % on the
uncorrected release and 0.1 % in both official sources), not the defect that
motivated it. The divergences the reallocation does not touch remain visible
and are the reason this table exists: land transport and post and
telecommunications overstated, chemicals and pharmaceuticals understated
threefold or more.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \
         .venv/bin/python -m analysis.figaro_recipe_validation
"""

import os
import pickle
import re

import numpy as np
import pandas as pd

from analysis.constants import BACKGROUND_YEAR, MODEL_LABEL
from paths import BRONZE_DIR, BACKGROUND_DIR, OUTPUT_DIR

# common reporting groups; each source is mapped onto them with its own codes
GROUPS_EXIO = [
    ("Water transport", r"sea and coastal|inland water"),
    ("Air transport", r"\bair transport\b"),
    ("Land transport and auxiliary", r"land transport|transport via|auxiliary transport|railway|pipeline"),
    ("Post and telecommunications", r"post and telecom"),
    ("Energy", r"electricity|gas works|steam and hot water|coke|refin"),
    ("Construction", r"construction"),
    ("Food and agriculture", r"food|beverages|meat|dairy|vegetables|cereal|farming|fish"),
    ("Chemicals and pharmaceuticals", r"chemical|pharma|plastic|rubber"),
    ("Business and other services", r"business activities|computer|research|financ|insur|legal|renting|real estate|hotel|membership|recreat"),
    ("Health and social work", r"health and social"),
]
GROUPS_FIGARO = [
    ("Water transport", r"^CPA_H50"),
    ("Air transport", r"^CPA_H51"),
    ("Land transport and auxiliary", r"^CPA_H49|^CPA_H52"),
    ("Post and telecommunications", r"^CPA_J61|^CPA_J58|^CPA_J59_60|^CPA_H53"),
    ("Energy", r"^CPA_D35|^CPA_B|^CPA_E36"),
    ("Construction", r"^CPA_F"),
    ("Food and agriculture", r"^CPA_A0|^CPA_C10"),
    ("Chemicals and pharmaceuticals", r"^CPA_C19|^CPA_C20|^CPA_C21|^CPA_C22"),
    ("Business and other services", r"^CPA_M|^CPA_N|^CPA_J62|^CPA_K6|^CPA_L|^CPA_O84|^CPA_G4"),
    ("Health and social work", r"^CPA_Q86|^CPA_Q87"),
]
GROUPS_DST = [
    ("Water transport", r"^50"), ("Air transport", r"^51"),
    ("Land transport and auxiliary", r"^49|^52|^53"),
    ("Post and telecommunications", r"^58|^61"),
    ("Energy", r"^35|^19"), ("Construction", r"^41|^42|^43"),
    ("Food and agriculture", r"^01|^02|^03|^10|^11|^12"),
    ("Chemicals and pharmaceuticals", r"^20|^21|^22"),
    ("Business and other services", r"^62|^63|^64|^65|^66|^68|^69|^70|^71|^72|^73|^74|^77|^78|^80|^81|^82"),
    ("Health and social work", r"^86|^87|^88"),
]


def _shares(
    values: np.ndarray,
    keys: list,
    groups: list[tuple[str, str]],
) -> dict[str, float]:
    """Aggregate a value vector into named groups by regex-matched key.

    Parameters
    ----------
    values : numpy.ndarray
        Values to sum, aligned one-to-one with ``keys``.
    keys : list
        Row labels (product or industry codes/names) tested against each
        group's pattern.
    groups : list of (str, str)
        ``(group_name, regex_pattern)`` pairs; a key is assigned to a group
        when its pattern matches (case-insensitively), and may match more
        than one group since group patterns are not mutually exclusive by
        construction here.

    Returns
    -------
    dict of str to float
        Each group's share of ``sum(values)`` as a percentage (0-100), plus
        an ``"Other"`` entry making the shares sum to 100. Zero when
        ``sum(values)`` is zero.
    """
    tot = float(np.sum(values))
    out = {}
    for name, pat in groups:
        rx = re.compile(pat, re.IGNORECASE)
        sel = [i for i, k in enumerate(keys) if rx.search(str(k))]
        out[name] = 100.0 * float(np.sum(np.asarray(values)[sel])) / tot if tot else 0.0
    out["Other"] = 100.0 - sum(out.values())
    return out


def main() -> None:
    """Compare the Danish health input recipe across EXIOBASE, FIGARO and DST.

    Aggregates the Danish health industry's intermediate-input structure into
    the ten common groups of the module docstring for three sources: the
    EXIOBASE Z-matrix column for Danish health and social work, Eurostat
    FIGARO's Q86 (human health) use-table rows, and Statistics Denmark's
    117-industry IO table columns 860010/860020, each as a percentage share.
    Writes
    ``data/gold/results/06_benchmarks_validation/recipe_validation_three_way.csv``
    and prints the comparison table. Reads ``HC_ANALYSIS_YEAR`` from the
    environment (default ``"2022"``) to select the FIGARO and DST source
    files; the EXIOBASE column is read from
    ``analysis.constants.BACKGROUND_YEAR``, which carries both that variable
    and ``HC_BACKGROUND_TAG``, so the recipe compared here is the one the
    headline tables are computed from.
    """
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    # --- EXIOBASE ---
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    with open(os.path.join(str(BACKGROUND_DIR), "pickled_mrio",
                           f"mrio{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        m = pickle.load(fh)
    Z = m["Z"]
    ind_names = list(bg["label"]["industry"]["Name"])
    col = Z[:, 6 * 163 + 137].reshape(49, 163).sum(axis=0)
    exio = _shares(col, ind_names, GROUPS_EXIO)

    # --- FIGARO (Q86 human health) ---
    fg = pd.read_csv(os.path.join(str(BRONZE_DIR), "eurostat_figaro",
                                  f"figaro2026_use_DKdest_{year}.csv"))
    # keep INTERMEDIATE inputs only: the FIGARO use table also carries primary
    # inputs (D1 compensation of employees, D21X31 taxes less subsidies,
    # B2A3G operating surplus), which are not part of an input recipe
    qf = fg[(fg["ind_use"] == "Q86") &
            (fg["prd_ava"].astype(str).str.startswith("CPA_"))]
    q = qf.groupby("prd_ava")["value"].sum()
    figaro = _shares(q.values, q.index, GROUPS_FIGARO)

    # --- DST 117-industry IO ---
    io = pd.read_excel(os.path.join(str(BRONZE_DIR), "dst_input_output",
                                    f"input_output_en_{year}.xlsx"),
                       sheet_name="IO", header=None, engine="openpyxl")
    codes = io.iloc[:, 0].astype(str).str.strip()
    hdr = [str(io.iat[2, j]).strip() for j in range(io.shape[1])]
    hcols = [j for j, h in enumerate(hdr) if h in ("860010", "860020")]
    rows = codes.str.fullmatch(r"\d{5,6}")
    vals = io.loc[rows, hcols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    dst = _shares(vals.to_numpy(float), codes[rows].tolist(), GROUPS_DST)

    df = pd.DataFrame({f"{MODEL_LABEL} (modelled)": exio,
                       "Eurostat FIGARO Q86 (official EU)": figaro,
                       "Statistics Denmark IO 86 (national)": dst}).round(1)
    df.index.name = "input_group_share_pct"
    out_dir = os.path.join(str(OUTPUT_DIR), "06_benchmarks_validation")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "recipe_validation_three_way.csv")
    df.to_csv(out)
    print(df.to_string())
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()
