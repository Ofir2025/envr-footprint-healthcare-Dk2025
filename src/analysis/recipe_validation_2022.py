# -*- coding: utf-8 -*-
"""Validate EXIOBASE's Danish health input recipe against the national IOT.

The healthcare-services footprint rests on the intermediate-input column of
EXIOBASE's DK "Health and social work" industry (the Steenmeijer Z-column
construction). Statistics Denmark's coupled-models report (Rormose Jensen &
Iliev 2022, pp. 11-12) documents that EXIOBASE's Danish block misallocates
water transport massively (74 % of output to Danish intermediate use vs 9 %
actual), which leaks shipping emissions into every Danish final-demand
footprint. This script reports what the recipe looks like in the background
the study actually runs on:

1. input composition of the DK health column of that background (grouped), vs
2. the aggregate input composition of the four health/care industries
   (860010, 860020, 870000, 880000) in the public DST 117-industry IOT
   (domestic + import rows, basic prices), grouped the same way;
3. the share of the healthcare GWP footprint occurring in Danish
   water-transport and Danish land-transport industries (hotspot side).

WHICH BACKGROUND THIS READS, AND WHY IT MATTERS. Both the MRIO and the
background are read at ``analysis.constants.BACKGROUND_YEAR``, so the recipe
and the hotspot shares printed beside it come from one model. Under
``HC_BACKGROUND_TAG=_snacship`` that is the reallocated model, and the water
transport row is then the *residual* after the correction rather than the
defect it was built to expose: 0.6 % against Statistics Denmark's 0.4 %,
where the uncorrected release gave 3.9 %. The size of the defect itself, and
what was moved to remove it, are layer 10's subject
(``10_sea_transport_reallocation/phantom_shipping_input_removed_by_industry.csv``).
What this table still shows on the corrected model is the part the
reallocation does not touch: land transport overstated about two and a half
times (17.0 % against 6.9 %), and chemicals and pharmaceuticals understated
about threefold (5.1 % against 14.9 %).

Run after the background exists:
    PYTHONPATH=src HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \
        .venv/bin/python -m analysis.recipe_validation_2022
"""

from __future__ import annotations

import pickle
import re

import numpy as np
import os
import pandas as pd

from analysis.constants import BACKGROUND_YEAR
from paths import BACKGROUND_DIR, BRONZE_DIR, MRIO_DIR, OUTPUT_DIR, SILVER_DIR

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


def _group_shares(
    values: np.ndarray, keys: list[str], groups: list[tuple[str, str]]
) -> dict[str, float]:
    """Aggregate a value vector into named groups by regex-matched key.

    Parameters
    ----------
    values : numpy.ndarray
        Values to sum, aligned one-to-one with ``keys``.
    keys : list of str
        Industry names or codes tested against each group's pattern.
    groups : list of (str, str)
        ``(group_name, regex_pattern)`` pairs.

    Returns
    -------
    dict of str to float
        Each group's share of ``sum(values)`` as a percentage (0-100), plus
        an ``"other"`` entry making the shares sum to 100. Zero when
        ``sum(values)`` is zero.
    """
    tot = float(np.sum(values))
    rows = {}
    for name, pat in groups:
        rx = re.compile(pat, re.IGNORECASE)
        sel = [i for i, k in enumerate(keys) if rx.search(k)]
        rows[name] = 100.0 * float(np.sum(values[sel])) / tot if tot else 0.0
    rows["other"] = 100.0 - sum(rows.values())
    return rows


def main() -> None:
    """Compare the EXIOBASE Danish health input recipe against the DST IOT.

    Groups the EXIOBASE 2022 DK health-industry Z-column and the aggregate
    input structure of the four DST health/care industries (860010, 860020,
    870000, 880000) into the ten common groups of the module docstring, both
    as percentage shares, and prints the comparison. Also reports the share
    of the healthcare GWP footprint occurring in Danish and worldwide
    transport industries (the hotspot side of the same discrepancy). Writes
    ``data/gold/results/06_benchmarks_validation/recipe_validation_2022.csv``.
    Both the MRIO and the background are read at
    ``analysis.constants.BACKGROUND_YEAR``, which carries both
    ``HC_ANALYSIS_YEAR`` and ``HC_BACKGROUND_TAG``, so the recipe and the
    hotspot shares beside it come from one and the same model variant.

    Raises
    ------
    AssertionError
        If the DST workbook does not resolve to exactly four health-industry
        columns.
    """
    with open(os.path.join(str(MRIO_DIR), f"mrio{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        m = pickle.load(fh)
    Z, x = m["Z"], m["x"][:, 0]
    ind_names = list(m["label"]["industry"]["Name"])
    nr, ns = 49, 163
    k_dk, k_health = 6, 137
    col = Z[:, k_dk * ns + k_health]
    col_by_sector = col.reshape(nr, ns).sum(axis=0)  # inputs by sector, all origins
    exio_shares = _group_shares(col_by_sector, ind_names, GROUPS_EXIO)

    io = pd.read_excel(BRONZE_DIR / "dst_input_output"
                       / "input_output_en_2022.xlsx",
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
    # Resolve through paths, not by walking up from the gold directory: bronze
    # and silver can be pointed elsewhere so two working copies share one copy
    # of them, and a hand-built relative path silently ignores that.
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"),
              "rb") as fh:
        bg = pickle.load(fh)
    B, L, Ystim = bg["B"], bg["L"], bg["Ystim"]
    x_tot = L @ Ystim[:, 0]
    e_by_node = B[0, :] * x_tot
    names_full = ind_names * nr
    dk_block = slice(k_dk * ns, (k_dk + 1) * ns)
    def _share(pat: str, block: slice | None = None) -> float:
        """Percentage of total healthcare GWP matching a node-name pattern.

        Parameters
        ----------
        pat : str
            Case-insensitive regex tested against each node's industry name.
        block : slice, optional
            Restrict matches to node indices within this slice (e.g. the
            Danish region block). Defaults to all regions.

        Returns
        -------
        float
            Percentage (0-100) of ``e_by_node.sum()`` found at matching
            nodes.
        """
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
    out_path = os.path.join(str(OUTPUT_DIR), "06_benchmarks_validation",
                            "recipe_validation_2022.csv")
    out.to_csv(out_path)
    print(f"\nwritten -> {out_path}")


def _dst_health_purchases(analysis_year: str = "2022") -> pd.DataFrame:
    """Purchases of the Danish health and care industries by product and origin.

    Hospital activities, medical and dental practice and residential care are taken in
    full and social work without accommodation (880000) at its elder-care share of that
    year, as in the study's boundary. The workbook's first block of product rows is
    Danish production and the second is imports, both at basic prices.

    Parameters
    ----------
    analysis_year : str
        Year of the published 117-industry input-output workbook.

    Returns
    -------
    pandas.DataFrame
        Columns ``origin`` (``"domestic"``, ``"import"``), ``dst_code`` and
        ``value`` (1000 DKK).
    """
    from analysis.extra_functions import eldercare_share_of_social_work_io
    path = BRONZE_DIR / "dst_input_output" / f"input_output_en_{analysis_year}.xlsx"
    alpha = eldercare_share_of_social_work_io(path)
    io = pd.read_excel(path, sheet_name="IO", header=None, engine="openpyxl")
    hdr = [str(io.iat[2, j]).strip() for j in range(io.shape[1])]
    weights = {"860010": 1.0, "860020": 1.0, "870000": 1.0, "880000": alpha}
    cols = {j: weights[h] for j, h in enumerate(hdr) if h in weights}
    assert len(cols) == 4, f"expected 4 health industry columns, found {len(cols)}"
    first = [str(v).strip() for v in io.iloc[:, 0]]
    imports_at = first.index("Imports")
    rows = []
    for i in range(io.shape[0]):
        code = first[i]
        if not re.fullmatch(r"\d{6}", code):
            continue
        v = sum(float(pd.to_numeric(io.iat[i, j], errors="coerce") or 0.0) * w for j, w in cols.items())
        rows.append(("import" if i > imports_at else "domestic", code, v))
    return pd.DataFrame(rows, columns=["origin", "dst_code", "value"])


#: Below this ratio of EXIOBASE spend to national spend in a product-and-origin cell,
#: EXIOBASE's own purchases are too thin to carry the national amount (scaling them
#: would put hospital medicines on whichever few nodes EXIOBASE happens to buy), so the
#: national amount is placed on the EXIOBASE sectors mapped to the product instead.
ROUTE_BELOW = 0.2


#: Danish products whose purchases stay at EXIOBASE's own amounts in the test: electricity,
#: gas and district heat. EXIOBASE v3.8.2 books most Danish combined heat-and-power
#: emissions to "Steam and hot water supply" while recording that industry's output at a
#: fifth of Statistics Denmark's (379 against 1,799 million euros in 2022), so each euro of
#: Danish district heat carries 18.7 kg CO2e directly in EXIOBASE against 0.24 kg in
#: Statistics Denmark's accounts (432 kt on 1,799 million euros, DRIVHUS 350030). Routing
#: the national heat purchases through that intensity adds 1,100 kt CO2e to the
#: ``national_recipe`` case (the ``national_recipe_with_heat`` row), an artefact of the
#: background, not of the recipe.
KEEP_AT_EXIOBASE = ("35",)


def _reweight(y: np.ndarray, codes: list[str], split: dict, nat: dict, part: dict,
              y_dk_fd: np.ndarray, x_out: np.ndarray, cells: set | None) -> tuple[np.ndarray, float]:
    """Move the services vector to national amounts in the chosen product-and-origin cells.

    Parameters
    ----------
    y : numpy.ndarray
        EXIOBASE services demand by node (million euros).
    codes : list of str
        EXIOBASE industry codes in node order within a region.
    split : dict
        EXIOBASE industry -> [(Danish product, output share, import share)].
    nat : dict
        (origin, Danish product) -> national amount (million euros), already scaled to the
        spend being re-weighted.
    part : dict
        (origin, Danish product) -> {node: EXIOBASE spend in that cell}.
    y_dk_fd, x_out : numpy.ndarray
        Danish final demand and gross output by node, the routing weights.
    cells : set or None
        Cells to move; None moves every cell in ``nat`` or ``part``.

    Returns
    -------
    y_new : numpy.ndarray
        The re-weighted vector.
    routed : float
        Spend placed on mapped sectors because EXIOBASE bought too little in the cell.
    """
    nr, ns, k_dk = 49, 163, 6
    todo = (set(part) | set(nat)) if cells is None else cells
    y_new = y.copy()
    for cell in todo:                     # take the cell's EXIOBASE spend out ...
        for k, v in part.get(cell, {}).items():
            y_new[k] -= v
    routed = 0.0
    for cell in todo:                     # ... and put the national amount back in
        target = nat.get(cell, 0.0)
        have = part.get(cell, {})
        spend = sum(have.values())
        if target == 0.0:
            continue
        if spend >= ROUTE_BELOW * target:
            for k, v in have.items():
                y_new[k] += v * target / spend
            continue
        origin, dcode = cell
        sectors = [i for i, c in enumerate(codes) if c in split and any(d == dcode for d, _, _ in split[c])]
        weights = {}
        for i in sectors:
            sh = [so if origin == "domestic" else si for d, so, si in split[codes[i]] if d == dcode][0]
            regions = [k_dk] if origin == "domestic" else [r for r in range(nr) if r != k_dk]
            for r in regions:
                weights[r * ns + i] = (y_dk_fd[r * ns + i], x_out[r * ns + i], sh if sh > 0 else 1.0)
        w = {k: fd * sh for k, (fd, xo, sh) in weights.items()}
        if sum(w.values()) <= 0:          # no Danish final demand for these nodes: use output
            w = {k: xo * sh for k, (fd, xo, sh) in weights.items()}
        wsum = sum(w.values())
        assert wsum > 0, f"nothing to route {cell} by"
        for k, wk in w.items():
            y_new[k] += target * wk / wsum
        routed += target
    return np.clip(y_new, 0.0, None), routed


def recipe_sensitivity() -> pd.DataFrame:
    """Footprint with the services purchases moved towards Statistics Denmark's own mix.

    The services component enters as the purchase column of EXIOBASE's Danish health
    and social work industry scaled to expenditure (the Steenmeijer construction), and
    :func:`main` shows that column's composition differs from the Danish national
    accounts: it buys about a third of the chemicals and almost none of the medicines
    that the Danish health industries buy, and about two and a half times the land
    transport. These sensitivity cases hold the services spend and every other term
    fixed and change the composition only.

    Method, in the classification of the Danish table (117 products, each split into
    domestic and imported supply):

    1. EXIOBASE's services purchases are mapped onto Danish products with the study's
       concordance (``exiobase_industry_to_dst_db07.csv``), splitting a one-to-many
       EXIOBASE industry by Danish output shares for Danish nodes and by Danish import
       shares for foreign nodes.
    2. The national amount of each product-and-origin cell is the Danish health
       industries' purchase share times the spend being re-weighted.
    3. Where EXIOBASE already buys at least ``ROUTE_BELOW`` of the national amount, its
       purchases in that cell are scaled to it; otherwise the national amount is placed
       on the EXIOBASE sectors mapped to the product (Danish nodes for domestic supply,
       foreign nodes for imports) in proportion to Danish final demand for each node.
       This is how hospital medicines, which EXIOBASE's column hardly buys, reach
       Chemicals n.e.c., the sector the study maps medicines to.
    4. The footprint of the vector is ``B L y`` on the study's background.

    Two cases are written. ``national_recipe`` moves every product except electricity,
    gas and district heat (``KEEP_AT_EXIOBASE``, for the reason given there).
    ``hospital_medicines`` moves only the pharmaceutical products (DB07 21), taking the
    spend they need proportionally from the rest of the column. ``both_corrections`` is
    that case with every medicine purchase on Chemicals n.e.c. (the added hospital
    medicines and the pharmaceutical component's own) carried at the pharmaceutical-
    specific intensity of the uncertainty analysis's Case B (``PHARMA_RATIO``, central
    value), because the second correction changes how much the first one adds.
    ``national_recipe_with_heat`` is a diagnostic, not a case: ``national_recipe`` with
    energy re-weighted too, whose difference from it is the heat artefact.

    Returns
    -------
    pandas.DataFrame
        One row per case and indicator, written to
        ``06_benchmarks_validation/recipe_sensitivity_2022.csv``.
    """
    from analysis.constants import (ROW_GWP, ROW_MATERIAL, ROW_WATER, ROW_LAND,
                                    ROW_WASTE, eriksen_folder)
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    B, L, Ystim, Y = bg["B"], bg["L"], bg["Ystim"], bg["Y"]
    nr, ns, k_dk = 49, 163, 6
    with open(os.path.join(str(MRIO_DIR), f"mrio{BACKGROUND_YEAR}.pkl"), "rb") as fh:
        mrio = pickle.load(fh)
    lab, x_out = mrio["label"], mrio["x"][:, 0]
    del mrio
    codes = [c.replace("A_", "", 1) for c in lab["industry"].index]
    y = Ystim[:, 1].astype(float)                      # services: the scaled health column
    total = float(y.sum())
    y_dk_fd = Y[:, k_dk * 7:(k_dk + 1) * 7].sum(axis=1)  # Danish final demand by node

    conc = pd.read_csv(SILVER_DIR / "classification_concordances"
                       / "exiobase_industry_to_dst_db07.csv", dtype=str)
    split: dict[str, list[tuple[str, float, float]]] = {}
    for _, r in conc.iterrows():
        if r["mapping_type"] == "unmatched" or pd.isna(r["dst_industry_code"]):
            continue
        dsts = r["dst_industry_code"].split(";")
        outs = [float(v) for v in str(r["dst_output_share"]).split(";")]
        imps = [float(v) for v in str(r["dst_import_share"]).split(";")]
        split[r["exiobase_code"]] = list(zip(dsts, outs, imps))

    part: dict[tuple[str, str], dict[int, float]] = {}
    for k in np.nonzero(y)[0]:
        code = codes[k % ns]
        origin = "domestic" if k // ns == k_dk else "import"
        for dst, so, si in split.get(code, []):
            w = so if origin == "domestic" else si
            if w > 0:
                part.setdefault((origin, dst), {})
                part[(origin, dst)][k] = part[(origin, dst)].get(k, 0.0) + y[k] * w
    dst = _dst_health_purchases("2022")
    dst = dst[dst["value"] > 0]
    mapped = {d for v in split.values() for d, _, _ in v}
    dst_unplaced = float(dst.loc[~dst["dst_code"].isin(mapped), "value"].sum() / dst["value"].sum())
    dst = dst[dst["dst_code"].isin(mapped)]

    kept = {c for c in set(part) | {(o, d) for o, d in zip(dst["origin"], dst["dst_code"])}
            if c[1].startswith(KEEP_AT_EXIOBASE)}
    kept_spend = sum(sum(part.get(c, {}).values()) for c in kept)
    in_scope = dst[~dst["dst_code"].str.startswith(KEEP_AT_EXIOBASE)]
    movable = sum(sum(v.values()) for c, v in part.items() if c not in kept)
    nat_all = {(o, c): v / in_scope["value"].sum() * movable
               for o, c, v in in_scope.itertuples(index=False)}
    cases = {}
    y_nat, routed_nat = _reweight(y, codes, split, nat_all, part, y_dk_fd, x_out,
                                  cells=(set(part) | set(nat_all)) - kept)
    y_nat *= total / y_nat.sum()            # rounding of shares and clipping: hold the spend
    cases["national_recipe"] = (y_nat, routed_nat)
    # diagnostic only: the same with electricity, gas and district heat re-weighted as
    # well, which measures the heat artefact described at KEEP_AT_EXIOBASE
    movable_all = sum(sum(v.values()) for v in part.values())
    nat_heat = {(o, c): v / dst["value"].sum() * movable_all
                for o, c, v in dst.itertuples(index=False)}
    y_heat, routed_heat = _reweight(y, codes, split, nat_heat, part, y_dk_fd, x_out,
                                    cells=set(part) | set(nat_heat))
    y_heat *= total / y_heat.sum()
    med_cells = {c for c in nat_all if c[1].startswith("21")}
    med = sum(nat_all[c] for c in med_cells)
    others = {c for c in part if c not in med_cells}
    y_pre = y.copy() * (1.0 - med / total)
    for c in med_cells:
        part_c = {k: v * (1.0 - med / total) for k, v in part.get(c, {}).items()}
        for k, v in part_c.items():
            y_pre[k] -= v
    y_med, routed_med = _reweight(y_pre, codes, split, {c: nat_all[c] for c in med_cells},
                                  {c: {} for c in med_cells}, y_dk_fd, x_out, cells=med_cells)
    scale = total / y_med.sum()
    added_med = (y_med - np.clip(y_pre, 0.0, None)) * scale   # the medicines placed, by node
    y_med *= scale
    cases["hospital_medicines"] = (y_med, routed_med)
    is_chem_nec = np.array([c == "CHEM" for c in codes] * nr)
    assert added_med[~is_chem_nec].max() < 1e-9 and added_med.min() > -1e-9, \
        "hospital medicines reached a sector other than Chemicals n.e.c."

    var = os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"))
    fig1 = pd.read_csv(os.path.join(var, "figure1_activity_contributions.csv"))
    rows_ix = {"climate_change": ROW_GWP, "material_extraction": ROW_MATERIAL,
               "blue_water_consumption": ROW_WATER, "land_use": ROW_LAND,
               "waste_generation": ROW_WASTE}
    from analysis.manuscript_figure_tables import figure_group_lookup
    ind_cls = pd.read_excel(BRONZE_DIR / "exiobase" / "classifications.xlsx",
                            sheet_name="disagg_ind", skiprows=5)
    ind_cls = ind_cls[ind_cls["Code"].astype(str).str.startswith("A_")]
    agg_of = dict(zip(ind_cls["Code"].str.replace("A_", "", n=1), ind_cls["AggDescription"]))
    look = figure_group_lookup()
    contrib_of = dict(zip(look["sector_group"], look["contribution_group"]))
    group_of = np.array([contrib_of.get(agg_of.get(c), "Other") for c in codes] * nr, dtype=object)
    chem = group_of == "Pharmaceuticals and chemical products"
    trans = group_of == "Transport"
    from analysis.uncertainty_2025 import PHARMA_RATIO, INDICATORS as U_IND
    ratio_of = {}
    for name, code in zip(U_IND, ["climate_change", "material_extraction", "blue_water_consumption",
                                  "land_use", "waste_generation"]):
        spec = PHARMA_RATIO[name]
        ratio_of[code] = spec["median"] if "median" in spec else sum(spec["uniform"]) / 2.0
    retail_med = Ystim[:, 2] * is_chem_nec            # the pharmaceutical component's medicines
    cases["both_corrections"] = (y_med, routed_med)
    cases["national_recipe_with_heat"] = (y_heat, routed_heat)
    groups_all = sorted(set(group_of))
    rows = []
    for case, (y_new, routed) in cases.items():
        assert abs(float(y_new.sum()) - total) < 1e-6 * total, f"{case}: the services spend changed"
        for ind, row in rows_ix.items():
            mult = B[row, :] @ L
            f_base, f_new = float(mult @ y), float(mult @ y_new)
            g = fig1[fig1["indicator"] == ind].set_index("contribution_group")["value"]
            head = float(g.sum())
            # every activity group: its services part moves with the case, the rest stays
            grp = {name: float(g.get(name, 0.0)) for name in g.index}
            for name in groups_all:
                m_ = group_of == name
                grp[name] = grp.get(name, 0.0) - float(mult[m_] @ y[m_]) + float(mult[m_] @ y_new[m_])
            if case == "both_corrections":
                r_ = ratio_of[ind]
                cut = (1.0 - r_) * (float(mult @ added_med) + float(mult @ retail_med))
                grp["Pharmaceuticals and chemical products"] -= cut
            total_new = sum(grp.values())
            f_new = f_base + (total_new - head)
            chem_new = grp.get("Pharmaceuticals and chemical products", 0.0)
            tr_new = grp.get("Transport", 0.0)
            leader = max(grp, key=grp.get)
            rows.append(dict(
                case=case, indicator=ind, services_footprint_headline=f_base,
                services_footprint_case=f_new, footprint_headline=head,
                footprint_case=total_new, change_pct=100.0 * (total_new - head) / head,
                pharma_chem_share_headline_pct=100.0 * float(g.get("Pharmaceuticals and chemical products", 0.0)) / head,
                pharma_chem_share_case_pct=100.0 * chem_new / total_new,
                transport_share_headline_pct=100.0 * float(g.get("Transport", 0.0)) / head,
                transport_share_case_pct=100.0 * tr_new / total_new,
                services_spend_meur=total, energy_spend_kept_meur=kept_spend,
                routed_spend_meur=routed, medicines_spend_meur=med,
                national_spend_without_counterpart_pct=100.0 * dst_unplaced,
                largest_group=leader, largest_group_share_pct=100.0 * grp[leader] / total_new,
            ))
    out = pd.DataFrame(rows)
    path = os.path.join(str(OUTPUT_DIR), "06_benchmarks_validation", "recipe_sensitivity_2022.csv")
    out.to_csv(path, index=False)
    print(out[["case", "indicator", "footprint_headline", "footprint_case", "change_pct",
               "pharma_chem_share_case_pct", "transport_share_case_pct", "largest_group",
               "largest_group_share_pct"]].round(2).to_string(index=False))
    print(f"\nwritten -> {path}")
    return out


if __name__ == "__main__":
    import sys as _sys
    if "--sensitivity" in _sys.argv:
        recipe_sensitivity()
    else:
        main()
