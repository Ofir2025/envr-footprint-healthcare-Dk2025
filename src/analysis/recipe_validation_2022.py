# -*- coding: utf-8 -*-
"""Validate EXIOBASE's Danish health input recipe against the national IOT.

The healthcare-services footprint rests on the intermediate-input column of
EXIOBASE's DK "Health and social work" industry (the Steenmeijer Z-column
construction). Statistics Denmark's coupled-models report (Rormose Jensen &
Iliev 2022, pp. 11-12) documents that EXIOBASE's Danish block misallocates
water transport massively (74% of output to Danish intermediate use vs 9%
actual), which leaks shipping emissions into every Danish final-demand
footprint. This script quantifies the discrepancy for healthcare:

1. input composition of the EXIOBASE 2022 DK health column (grouped), vs
2. the aggregate input composition of the four health/care industries
   (860010, 860020, 870000, 880000) in the public DST 117-industry IOT 2022
   (domestic + import rows, basic prices), grouped the same way;
3. the share of the healthcare GWP footprint occurring in Danish
   water-transport and Danish land-transport industries (hotspot side).

Run after the 2022 background exists:
    PYTHONPATH=src .venv/bin/python -m analysis.recipe_validation_2022
"""

import pickle
import re

import numpy as np
import pandas as pd

from paths import BRONZE_DIR, MRIO_DIR, OUTPUT_DIR

GROUPS_EXIO = [
    ("water transport", r"sea and coastal|inland water"),
    ("air transport", r"\bair transport\b"),
    ("land transport & aux", r"land transport|transport via|auxiliary transport|railway|pipeline"),
    ("post & telecom", r"post and telecom"),
    ("energy", r"electricity|gas works|steam and hot water|coke|refin"),
    ("construction", r"construction"),
    ("food & agri", r"food|beverages|meat|dairy|vegetables|cereal|farming|fish"),
    ("chemicals & pharma", r"chemical|pharma|plastic|rubber"),
    ("business & other services", r"business activities|computer|research|financ|insur|legal|renting|real estate|hotel|membership|recreat"),
    ("health & social", r"health and social"),
]
GROUPS_DST = [
    ("water transport", r"^50"),
    ("air transport", r"^51"),
    ("land transport & aux", r"^49|^52|^53"),
    ("post & telecom", r"^58|^61"),
    ("energy", r"^35|^19"),
    ("construction", r"^41|^42|^43"),
    ("food & agri", r"^01|^02|^03|^10|^11|^12"),
    ("chemicals & pharma", r"^20|^21|^22"),
    ("business & other services", r"^62|^63|^64|^65|^66|^68|^69|^70|^71|^72|^73|^74|^77|^78|^80|^81|^82"),
    ("health & social", r"^86|^87|^88"),
]


def _group_shares(values, keys, groups):
    tot = float(np.sum(values))
    rows = {}
    for name, pat in groups:
        rx = re.compile(pat, re.IGNORECASE)
        sel = [i for i, k in enumerate(keys) if rx.search(k)]
        rows[name] = 100.0 * float(np.sum(values[sel])) / tot if tot else 0.0
    rows["other"] = 100.0 - sum(rows.values())
    return rows


def main():
    with open(str(MRIO_DIR) + "/mrio2022.pkl", "rb") as fh:
        m = pickle.load(fh)
    Z, x = m["Z"], m["x"][:, 0]
    ind_names = list(m["label"]["industry"]["Name"])
    nr, ns = 49, 163
    k_dk, k_health = 6, 137
    col = Z[:, k_dk * ns + k_health]
    col_by_sector = col.reshape(nr, ns).sum(axis=0)  # inputs by sector, all origins
    exio_shares = _group_shares(col_by_sector, ind_names, GROUPS_EXIO)

    io = pd.read_excel(BRONZE_DIR / "input_output" / "2016_2022" / "input_output_en_2022.xlsx",
                       sheet_name="IO", header=None, engine="openpyxl")
    codes = io.iloc[:, 0].astype(str).str.strip()
    labels = io.iloc[:, 1].astype(str).str.strip()
    health_cols = [j for j in range(2, 119)
                   if str(io.iat[1, j]).strip() in ("860010", "860020", "870000", "880000")
                   or str(io.iat[2, j]).strip() in ("860010", "860020", "870000", "880000")]
    if not health_cols:  # header layout: industry codes on row 2 (0-based row index 2)
        hdr = [str(io.iat[2, j]).strip() for j in range(io.shape[1])]
        health_cols = [j for j, h in enumerate(hdr) if h in ("860010", "860020", "870000", "880000")]
    assert len(health_cols) == 4, f"expected 4 health industry columns, found {len(health_cols)}"

    rows_num = codes.str.fullmatch(r"\d{5,6}")
    vals = io.loc[rows_num, health_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    keys = codes[rows_num].tolist()  # 6-digit DB07 codes (domestic + import rows)
    dst_shares = _group_shares(vals.to_numpy(dtype=float), keys, GROUPS_DST)

    out = pd.DataFrame({"EXIOBASE 2022 DK health column (%)": exio_shares,
                        "DST IOT 2022 health industries (%)": dst_shares}).round(1)
    print("\nInput-recipe comparison (shares of intermediate inputs):")
    print(out.to_string())

    # hotspot side: healthcare GWP arising in Danish transport industries
    with open(str(OUTPUT_DIR) + "/../../silver/background/gddz_background_information_2022.pkl", "rb") as fh:
        bg = pickle.load(fh)
    B, L, Ystim = bg["B"], bg["L"], bg["Ystim"]
    x_tot = L @ Ystim[:, 0]
    e_by_node = B[0, :] * x_tot
    names_full = ind_names * nr
    dk_block = slice(k_dk * ns, (k_dk + 1) * ns)
    def _share(pat, block=None):
        rx = re.compile(pat, re.IGNORECASE)
        idx = [i for i, nm in enumerate(names_full) if rx.search(nm)]
        if block is not None:
            idx = [i for i in idx if block.start <= i < block.stop]
        return 100.0 * float(e_by_node[idx].sum()) / float(e_by_node.sum())
    print(f"\nShare of healthcare MRIO GWP occurring in:")
    print(f"  Danish water-transport industries : {_share(r'sea and coastal|inland water', dk_block):5.1f} %")
    print(f"  Danish land-transport industries  : {_share(r'land transport|transport via', dk_block):5.1f} %")
    print(f"  ALL water-transport (any region)  : {_share(r'sea and coastal|inland water'):5.1f} %")
    print(f"  ALL transport industries          : {_share(r'transport'):5.1f} %")
    out.to_csv(str(OUTPUT_DIR) + "/recipe_validation_2022.csv")
    print(f"\nwritten -> {OUTPUT_DIR}/recipe_validation_2022.csv")


if __name__ == "__main__":
    main()
