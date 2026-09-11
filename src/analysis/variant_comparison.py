# -*- coding: utf-8 -*-
"""Put every model variant side by side, in one table, for every indicator.

Motivation
----------
``01_eriksen_replication/`` publishes one folder per model variant, and a variant
fixes the four axes that change the numbers: EXIOBASE release, Danish
sea-transport correction, care boundary, and capital treatment. A reader who
wants to know what each axis costs has to open eight folders and read the same
cell out of each, and a reader who wants that for an indicator other than climate
has to do it five times over. The comparison was consequently written out by hand
into the documentation, in climate only, where it went stale: the manuscript
table carried the pre-AR6 climate totals for three variants after the 2016
backgrounds were republished on IPCC AR6.

This module writes the comparison instead, one row per variant and indicator,
every cell read from that variant's own published tables. Nothing here recomputes
a footprint; if a variant's folder changes, this table changes with it.

Where each column comes from
----------------------------
================================  =========================================
column                            source
================================  =========================================
the four axes, ``role``           ``constants.variant_axes``, keyed on the
                                  folder name
``exiobase_release``,             parsed out of the ``model`` string the
``exiobase_table_year``           variant's own gold rows carry, so the
                                  release is read from the run rather than
                                  from a constant that could disagree with it
``healthcare_footprint``,         ``table_s05_dk.csv``
``national_footprint``,
``healthcare_share_pct``
``transport_share_pct``           ``figure2_sector_contributions.csv``,
                                  the ``Transport`` producing-sector group
``expenditure_meur``              ``table_01.csv``, ``Total`` row
================================  =========================================
"""

from __future__ import annotations

import re

import pandas as pd

from analysis.constants import variant_axes
from paths import OUTPUT_DIR

#: The layer whose variant folders are compared.
FOLDER = "01_eriksen_replication"

#: Output, at the layer root beside the folders it summarises.
COMPARISON_CSV = "variant_comparison.csv"

#: The producing-sector group whose share the manuscript's transport finding is
#: about.
TRANSPORT_GROUP = "Transport"

#: ``table_s05_dk.csv`` indexes indicators by their display name. This maps them
#: onto the machine names the rest of the layer uses.
INDICATOR_OF_ROW: dict[str, tuple[str, str]] = {
    "Global warming (ktCO2eq)": ("climate_change", "kt CO2-eq"),
    "Material extraction (kt)": ("material_extraction", "kt"),
    "Blue water consumption (Mm3)": ("blue_water_consumption", "Mm3"),
    "Land use (km2)": ("land_use", "km2"),
    "Waste generation (kt)": ("waste_generation", "kt"),
}

#: What each configuration is for, in one phrase. Keyed on the folder name
#: because the two unlettered configurations have no letter to key on.
ROLE: dict[str, str] = {
    "2019a": "the configuration the manuscript was submitted on",
    "2019b": "the submitted configuration plus the Danish shipping correction",
    "2019c": "2019 on the current release, comparable with 2022c",
    "2019d": "2019 on the widest boundary, comparable with Schmidt & Merciai",
    "2022c": "the headline of the resubmission",
    "2022d": "the widest boundary, comparable with Schmidt & Merciai (2023)",
    "2019_uncorrected": "the only configuration reproducing the submitted "
                        "transport finding; NOT variant a",
    "2022_uncorrected": "2022 without the shipping correction, for the bridge",
}


def model_axes(model: str) -> tuple[str, str]:
    """Read the EXIOBASE release and table year out of a model string.

    Parameters
    ----------
    model : str
        A ``model`` cell as the gold tables carry it, e.g.
        ``"EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport ..."``.

    Returns
    -------
    tuple of str
        Release (``"v3.8.2"``) and EXIOBASE table year (``"2022"``).

    Raises
    ------
    ValueError
        If either cannot be read. A variant whose own rows do not say which
        release produced them is a provenance failure, not a formatting one.
    """
    release = re.search(r"EXIOBASE (v[\d.]+)", model)
    table = re.search(r"IOT_(\d{4})_ixi", model)
    if not release or not table:
        raise ValueError(f"cannot read release and table year from {model!r}")
    return release.group(1), table.group(1)


def variant_row(folder: str) -> list[dict[str, object]]:
    """Build one row per indicator for a single variant folder.

    Parameters
    ----------
    folder : str
        Variant folder name, e.g. ``"2019a"``.

    Returns
    -------
    list of dict
        One record per indicator in :data:`INDICATOR_OF_ROW`.

    Raises
    ------
    ValueError
        If the folder name is not a known variant.
    """
    axes = variant_axes(folder)
    if axes is None:
        raise ValueError(f"{folder} is not a variant folder")
    path = OUTPUT_DIR / FOLDER / folder
    model = str(pd.read_csv(path / "hotspot_by_producing_node.csv",
                            nrows=1).iloc[0]["model"])
    release, table_year = model_axes(model)

    shares = pd.read_csv(path / "table_s05_dk.csv", index_col=0)
    totals = pd.read_csv(path / "table_01.csv", index_col=0)
    sectors = pd.read_csv(path / "figure2_sector_contributions.csv")

    rows: list[dict[str, object]] = []
    for display, (indicator, unit) in INDICATOR_OF_ROW.items():
        share_row = shares.loc[display]
        transport = sectors[(sectors.indicator == indicator)
                            & (sectors.hotspot_group == TRANSPORT_GROUP)]
        rows.append({
            "variant": folder,
            "analysis_year": folder[:4],
            "exiobase_release": release,
            "exiobase_table_year": table_year,
            "shipping_correction": "yes" if axes["tag"] else "no",
            "care_boundary": ("health care plus child and elder care"
                              if axes["scope"] == "zorg_en_welzijn"
                              else "health care"),
            "capital_treatment": axes["capital"],
            "role": ROLE.get(folder, ""),
            "indicator": indicator,
            "unit": unit,
            "healthcare_footprint": float(share_row.iloc[0]),
            "national_footprint": float(share_row.iloc[1]),
            "healthcare_share_pct": float(share_row.iloc[2]),
            "transport_share_pct": (float(transport.share_pct.iloc[0])
                                    if len(transport) else float("nan")),
            "expenditure_meur": float(totals.loc["Total",
                                                 "Expenditure (MEUR)"]),
        })
    return rows


def build_comparison() -> pd.DataFrame:
    """Build the cross-variant comparison over every published variant folder.

    Returns
    -------
    pandas.DataFrame
        One row per variant and indicator, ordered by analysis year, then
        variant, then the indicator order of :data:`INDICATOR_OF_ROW`.

    Raises
    ------
    FileNotFoundError
        If the layer holds no variant folder.
    """
    layer = OUTPUT_DIR / FOLDER
    folders = sorted(p.name for p in layer.iterdir()
                     if p.is_dir() and variant_axes(p.name) is not None)
    if not folders:
        raise FileNotFoundError(f"no variant folder under {layer}")
    rows: list[dict[str, object]] = []
    for folder in folders:
        rows.extend(variant_row(folder))
    frame = pd.DataFrame(rows)
    order = {name: i for i, (_, (name, _))
             in enumerate(INDICATOR_OF_ROW.items())}
    frame["_i"] = frame.indicator.map(order)
    return (frame.sort_values(["analysis_year", "variant", "_i"])
            .drop(columns="_i").reset_index(drop=True))


def main() -> None:
    """Write the comparison and print its climate slice."""
    comparison = build_comparison()
    out = OUTPUT_DIR / FOLDER / COMPARISON_CSV
    comparison.to_csv(out, index=False)

    climate = comparison[comparison.indicator == "climate_change"]
    show = ["variant", "exiobase_release", "exiobase_table_year",
            "shipping_correction", "capital_treatment",
            "healthcare_footprint", "healthcare_share_pct",
            "transport_share_pct"]
    print(climate[show].to_string(index=False,
                                  float_format=lambda v: f"{v:,.2f}"))
    print(f"\n{len(comparison)} rows, {comparison.variant.nunique()} variants "
          f"x {comparison.indicator.nunique()} indicators")
    print(f"written -> {out}")


if __name__ == "__main__":
    main()
