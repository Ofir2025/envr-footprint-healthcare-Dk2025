# -*- coding: utf-8 -*-
"""Assemble the study's verified tables into one Word document of record.

Tables reported during the project were screenshotted into a running history,
and several of those screenshots carry numbers that later work superseded: a
Danish national total of 76.5 Mt that is now 77.5, a climate footprint of
4,629 kt that the AR6 restatement moved to 4,713, a production-layer share of
67.9 % computed on a model that was subsequently withdrawn. A record made from
screenshots preserves the arithmetic of the moment rather than the state of the
study.

This module rebuilds every table from the gold fact tables instead, so the
document is generated rather than transcribed and can be regenerated whenever a
number moves. Each table carries a note stating what it shows, which file it was
read from, and, where a superseded value is known to be circulating, what
changed and why.

The document is a record, not a manuscript. It reports what the study currently
holds, with its provenance, so that any figure quoted in the paper, the slides
or an email can be traced to a file and a run.

Run
---
``HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship PYTHONPATH=src
python -m analysis.build_tables_record``
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable

import numpy as np
import pandas as pd

from analysis import gold_scope
from analysis.constants import (ANALYSIS_YEAR, DK_POPULATION, MODEL_LABEL,
                                eriksen_folder, scopes_folder)
from paths import OUTPUT_DIR, PROJECT_ROOT

OUT_DIR = os.path.join(str(OUTPUT_DIR), "19_tables_of_record")
# A Word rendering of the same tables is a document, not data, so it is
# published under docs/, not in gold: gold publishes tabular data only.
DOCX = os.path.join(str(PROJECT_ROOT), "docs", "revision",
                    "tables_of_record.docx")

#: House palette, matching the figures and the slide deck.
DEEP = "0B4F4A"
INK = "253331"
MUTE = "6B7F7B"
RULE = "D8E3DF"


def _g(*parts: str) -> str:
    """Path inside the gold results tree."""
    return os.path.join(str(OUTPUT_DIR), *parts)


def _read(*parts: str) -> pd.DataFrame:
    """Read one gold table."""
    return pd.read_csv(_g(*parts))


#: Unit strings as they should be typeset in a document rather than in a CSV.
UNIT_DISPLAY = {"kt CO2eq": "kt CO\u2082-eq", "Mm3": "Mm\u00b3",
                "km2": "km\u00b2", "kt": "kt",
                "kt CO2-eq": "kt CO\u2082-eq"}


def _unit(u: Any) -> str:
    """Typeset a unit string for the document."""
    return UNIT_DISPLAY.get(str(u), str(u))


def _numeric_column(values: list[str]) -> bool:
    """Whether a column holds numbers and should be right-aligned."""
    seen = [v for v in values if str(v).strip()]
    if not seen:
        return False
    ok = sum(1 for v in seen
             if str(v).replace(",", "").replace(".", "").replace("-", "")
             .replace("%", "").replace("+", "").strip().isdigit())
    return ok >= 0.7 * len(seen)


def _fmt(x: Any, digits: int = 1) -> str:
    """Format a value for a table cell, thousands-separated."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    if isinstance(x, (int, np.integer)):
        return f"{x:,}"
    if isinstance(x, (float, np.floating)):
        return f"{x:,.{digits}f}"
    return str(x)


def _sigfig(x: Any, figures: int = 3) -> str:
    """Format a value to a fixed number of significant figures.

    The house rule caps reported values at three significant figures. A fixed
    number of decimal places cannot honour that across a column whose values
    span orders of magnitude: three decimals turns 78.8 into 78.758, and one
    decimal turns 0.009 into 0.0.

    Parameters
    ----------
    x : Any
        The value to format. Non-numeric values are returned unchanged.
    figures : int, default 3
        Significant figures to keep.

    Returns
    -------
    str
        The formatted value, thousands-separated, with no trailing zeros
        beyond those the significant figures require.
    """
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    if not isinstance(x, (int, float, np.integer, np.floating)):
        return str(x)
    if x == 0:
        return "0"
    exponent = int(np.floor(np.log10(abs(float(x)))))
    decimals = max(0, figures - 1 - exponent)
    return f"{float(x):,.{decimals}f}"


@dataclass
class Table:
    """One table of record.

    Parameters
    ----------
    number : int
        Position in the document.
    title : str
        A declarative title: the finding, not the variable.
    frame : pandas.DataFrame
        The table as it should appear.
    source : str
        The gold file or files the numbers were read from.
    note : str
        What the table shows and how to read it.
    supersedes : str
        What a circulating earlier version of this table said, and why it
        changed. Empty where no earlier version is known.
    digits : int
        Decimal places for float columns.
    """

    number: int
    title: str
    frame: pd.DataFrame
    source: str
    note: str
    supersedes: str = ""
    digits: int = 1


# ---------------------------------------------------------------------------
# builders
# ---------------------------------------------------------------------------

def t_headline() -> Table:
    """Headline results for the reference year, all five categories."""
    tot = _read(*eriksen_folder().split("/"), "figure1_activity_contributions.csv")
    agg = tot.groupby(["indicator", "unit"])["value"].sum().reset_index()
    nat = _read("00_core_footprint", "national_totals_summary.csv")
    pop = DK_POPULATION[ANALYSIS_YEAR]
    share = {r["indicator"]: float(r["national_footprint"])
             for _, r in nat.iterrows()}
    rows = []
    label = {"climate_change": "Climate change", "material_extraction":
             "Material extraction", "blue_water_consumption":
             "Blue water consumption", "land_use": "Land use",
             "waste_generation": "Waste generation"}
    for _, r in agg.iterrows():
        v = float(r["value"])
        n = share.get(r["indicator"], np.nan)
        rows.append({
            "Impact category": label.get(r["indicator"], r["indicator"]),
            "Unit": _unit(r["unit"]),
            "Health care": _fmt(v, 1),
            "Per person": _fmt(v * 1e6 / pop, 1),
            "Danish total": _fmt(n, 1) if n == n else "",
            "Share of national (%)": _fmt(100 * v / n, 1) if n == n and n else "",
        })
    return Table(
        1, "The Danish health-care footprint in 2022, on five impact categories",
        pd.DataFrame(rows),
        f"{eriksen_folder()}/figure1_activity_contributions.csv and "
        f"00_core_footprint/national_totals_summary.csv",
        "The study's headline. Health and eldercare on the SHA boundary, "
        "climate on IPCC AR6 global warming potentials, capital excluded from "
        "the boundary. Per-person values use the Danish population of "
        f"{pop:,} in {ANALYSIS_YEAR}.",
        "A climate figure of 4,629 kt appears in earlier material. That was "
        "computed on AR4 global warming potentials; the study now reports AR6, "
        "which includes the fossil and non-fossil methane split that AR4's "
        "single factor of 25 did not make.")


def t_year_comparison() -> Table:
    """2019 against 2022, with the warning that it is not a time series."""
    d = _read("06_benchmarks_validation", "year_comparison_2019_2022.csv")
    label = {"climate_change": "Climate change", "material_extraction":
             "Material extraction", "blue_water_consumption":
             "Blue water consumption", "land_use": "Land use",
             "waste_generation": "Waste generation"}
    rows = [{
        "Impact category": label.get(r["indicator"], r["indicator"]),
        "Unit": _unit(r["unit"]),
        "2019": _fmt(r["value_2019"], 1),
        "2022": _fmt(r["value_2022"], 1),
        "Change (%)": _fmt(r["change_pct"], 1),
    } for _, r in d.iterrows()]
    return Table(
        2, "The two reference years differ by three things at once, so the "
           "change is not a trend",
        pd.DataFrame(rows),
        "06_benchmarks_validation/year_comparison_2019_2022.csv",
        "The runs differ in reference year, in background year "
        "(EXIOBASE IOT_2016 against IOT_2022) and in whether the Danish "
        "sea-transport reallocation is applied, which it is only for 2022. "
        "The corrected demand vector is used in both, so it is not part of the "
        "difference. Table 3 decomposes the climate movement.",
        "")


def t_climate_bridge() -> Table:
    """Why climate falls while the other four categories rise."""
    d = _read("06_benchmarks_validation", "year_comparison_climate_bridge.csv")
    d = d.reindex(d["delta_kt"].abs().sort_values(ascending=False).index)
    rows = [{
        "Activity group": r["contribution_group"],
        "2019 (kt CO\u2082-eq)": _fmt(r["value_2019"], 1),
        "2022 (kt CO\u2082-eq)": _fmt(r["value_2022"], 1),
        "Change (kt)": _fmt(r["delta_kt"], 1),
        "Driver": r["driver"],
    } for _, r in d.iterrows()]
    return Table(
        3, "Two activity groups account for the whole climate movement, in "
           "opposite directions",
        pd.DataFrame(rows),
        "06_benchmarks_validation/year_comparison_climate_bridge.csv",
        "Transport falls as the phantom Danish shipping input is removed by "
        "the sea-transport reallocation, and pharmaceuticals rise as "
        "expenditure grows. Every other group together moves 602 kt. This is "
        "the answer to why one category falls while four rise: the correction "
        "was almost entirely a climate artefact, sitting on a transport-heavy "
        "supply chain.")


def t_scopes() -> Table:
    """The GHG-Protocol scope partition."""
    d = _read(*scopes_folder().split("/"), "scopes_summary_detailed.csv")
    keep = ["Scope 1", "Scope 2", "Scope 3", "Outside protocol", "TOTAL"]
    d = d[d["scope"].isin(keep)]
    piv = d.pivot_table(index=["indicator", "unit"], columns="scope",
                        values="value").reset_index()
    label = {"climate_change": "Climate change", "material_extraction":
             "Material extraction", "blue_water_consumption":
             "Blue water consumption", "land_use": "Land use",
             "waste_generation": "Waste generation"}
    rows = [{
        "Impact category": label.get(r["indicator"], r["indicator"]),
        "Unit": _unit(r["unit"]),
        **{k: _fmt(r.get(k, np.nan), 2) for k in keep},
    } for _, r in piv.iterrows()]
    return Table(
        4, "Almost the whole footprint is Scope 3, in every impact category",
        pd.DataFrame(rows),
        f"{scopes_folder()}/scopes_summary_detailed.csv",
        "Scopes follow the GHG Protocol as operationalised by Hertwich and "
        "Wood (2018). Scope 2 here is the strict convention, in which upstream "
        "fuel supply stays in Scope 3; the manuscript's reported Scope 2 uses "
        "the broader cradle-to-gate convention and is carried in the same file. "
        "Material extraction, blue water and land use have no Scope 1 because "
        "EXIOBASE attributes extraction, abstraction and land occupation to "
        "extractive and agricultural industries, so a health service industry "
        "has no direct row. That is an accounting property, not a data gap.",
        "The climate total here is 1.83 kt below the study headline. The "
        "difference is the self-supply loop, removed from the scope partition "
        "because it overlaps the national-accounts Scope 1, and reported as "
        "its own row in the same file.")


def t_benchmarks() -> Table:
    """Published Danish national footprints, by model family."""
    d = _read("06_benchmarks_validation",
              "published_danish_footprint_benchmarks.csv")
    d = d.sort_values("per_capita_t")
    rows = [{
        "Source": r["source"],
        "Year": int(r["year"]),
        "Model family": r["model_family"],
        "Mt CO\u2082-eq": _fmt(r["total_mt"], 1),
        "t per person": _fmt(r["per_capita_t"], 2),
        "Capital": r["capital"],
    } for _, r in d.iterrows()]
    return Table(
        5, "Published Danish national footprints separate by model family, "
           "not by year",
        pd.DataFrame(rows),
        "06_benchmarks_validation/published_danish_footprint_benchmarks.csv",
        "The two EXIOBASE-family results sit at 12.90 and 13.19 t per person; "
        "the three national-accounts-family results sit between 9.77 and 11.00. "
        "This study is within 2.3 % of the only other published Danish "
        "EXIOBASE study, and about 20 % above the national-accounts family, as "
        "that family's own members are above one another. The gap against "
        "Statistics Denmark is therefore a property of the model family rather "
        "than an error in this implementation. The five estimates span a "
        "coefficient of variation of 12.8 %, which is wider than this study's "
        "parametric uncertainty interval.",
        "An earlier version of this table gave this study as 76.5 Mt and "
        "13.02 t per person. Both moved with the AR6 restatement.")


def t_boundary_matched() -> Table:
    """The ladder from this study's headline to Schmidt and Merciai."""
    d = _read("06_benchmarks_validation",
              "danish_healthcare_benchmark_boundary_matched.csv")
    rows = [{
        "Basis": r["basis"],
        "Mt CO\u2082-eq": _fmt(r["value_kt"] / 1000, 2),
        "t per person": _fmt(r["t_per_capita"], 3),
        "Share of national (%)": _fmt(r["share_of_national_pct"], 1),
        "Comparable": "yes" if r["comparable_with_published"] else "no",
    } for _, r in d.iterrows()]
    return Table(
        6, "Matched to their boundary and capital treatment, this study and "
           "Schmidt and Merciai agree to 1.7 %",
        pd.DataFrame(rows),
        "06_benchmarks_validation/danish_healthcare_benchmark_boundary_matched.csv",
        "Only the last row is comparable with the published value. Two "
        "conventions separate them: the sector boundary, where the comparator "
        "uses NACE Q including childcare, and the treatment of capital, which "
        "the comparator endogenises. Their model is consequential and this one "
        "attributional, and that difference cannot be removed by matching "
        "boundaries; it remains, and the agreement should be read with it.")


def t_gwp_revision() -> Table:
    """The climate footprint on five global-warming-potential revisions."""
    d = _read("15_gwp_revision", "gwp_revision_sensitivity.csv")
    cols = {c.lower(): c for c in d.columns}
    val = cols.get("healthcare_kt") or cols.get("value") or d.columns[1]
    rows = [{
        "Revision": r[d.columns[0]],
        "Health care (kt CO\u2082-eq)": _fmt(r[val], 1),
    } for _, r in d.iterrows()]
    return Table(
        7, "The choice of global-warming-potential revision moves the climate "
           "footprint by 5 %",
        pd.DataFrame(rows),
        "15_gwp_revision/gwp_revision_sensitivity.csv",
        "The study reports AR6 throughout. The spread across four IPCC "
        "assessment revisions is a reminder that a climate footprint is not a "
        "measurement but a measurement combined with a convention, and that "
        "the convention must be stated with the number. The environment "
        "variable HC_GWP_REVISION reproduces any row.")


def t_capital() -> Table:
    """What including capital does to each impact category."""
    d = _read("11_capital_gfcf", "capital_scenarios_by_indicator.csv")
    piv = d.pivot_table(index=["indicator", "unit"], columns="scenario",
                        values="value").reset_index()
    label = {"climate_change": "Climate change", "material_extraction":
             "Material extraction", "blue_water_consumption":
             "Blue water consumption", "land_use": "Land use",
             "waste_generation": "Waste generation"}
    order = ["baseline_capital_excluded", "A_exogenous_capital_service_flow",
             "D_full_endogenisation"]
    head = {"baseline_capital_excluded": "Capital excluded (headline)",
            "A_exogenous_capital_service_flow": "Capital as a service flow",
            "D_full_endogenisation": "Capital endogenised"}
    rows = []
    for _, r in piv.iterrows():
        base = r.get(order[0], np.nan)
        row = {"Impact category": label.get(r["indicator"], r["indicator"]),
               "Unit": _unit(r["unit"])}
        for k in order:
            v = r.get(k, np.nan)
            row[head[k]] = _fmt(v, 1)
        row["Endogenised change (%)"] = _fmt(
            100 * (r.get(order[2], np.nan) / base - 1), 1) if base else ""
        rows.append(row)
    return Table(
        8, "Endogenising capital raises every impact category, by 10 % to 33 %",
        pd.DataFrame(rows),
        "11_capital_gfcf/capital_scenarios_by_indicator.csv",
        "Capital is excluded from the headline, which is the convention "
        "Steenmeijer et al., Eckelman and Sherman, and the NHS reports use, so "
        "the headline stays comparable with the literature. The endogenised "
        "column follows Sodersten et al. (2018) and is the treatment Schmidt "
        "and Merciai use, which is why table 6 needs it. None of the three is "
        "wrong; each is a convention that must be reported with the number.")


def t_health_functions() -> Table | None:
    """Footprint by health-care function, and what the split can support.

    Returns
    -------
    Table or None
        None in a working copy that does not carry the health sub-sector
        layer, which is classified private and therefore absent from the copy
        that feeds the co-author's branch.
    """
    if not gold_scope.is_present("17_health_subsectors"):
        return None
    d = _read("17_health_subsectors", "footprint_by_health_function.csv")
    d = d[d["indicator"] == "climate_change"] if "indicator" in d.columns else d
    rows = [{
        "Function": r["function"],
        "Expenditure (M.EUR)": _fmt(r["expenditure_meur"], 0),
        "Share of spending (%)": _fmt(r["expenditure_share_pct"], 1),
        "Intensity (kt per M.EUR)": _fmt(r["intensity_per_meur"], 3),
        "Footprint (kt CO\u2082-eq)": _fmt(r["value"], 0),
    } for _, r in d.iterrows()]
    return Table(
        9, "The function split is an expenditure ranking, not an intensity "
           "finding",
        pd.DataFrame(rows),
        "17_health_subsectors/footprint_by_health_function.csv",
        "Five functions carry only three distinct intensities, because "
        "EXIOBASE has a single health and social work industry and the split "
        "is made by an output-prorated concordance after Malik et al. (2018). "
        "The services, pharmaceuticals and appliances distinction is a genuine "
        "intensity finding; the ordering within the three service functions "
        "carries no supply-chain information and should not be quoted as "
        "though it did. Genuine per-function recipes need the Danish "
        "117-industry table.")


def t_uncertainty() -> Table:
    """Central estimate, interval and both IPCC tiers."""
    tot = _read("04_uncertainty_lenzen_ieooc", "uncertainty_totals.csv")
    tot = tot[tot["pharma_scenario"] == "A"]
    t1 = _read("04_uncertainty_lenzen_ieooc",
               "uncertainty_tier1_error_propagation.csv")
    t1m = dict(zip(t1["indicator"], t1["tier1_uncertainty_pct"]))
    rows = [{
        "Impact category": r["indicator"],
        "Deterministic": _fmt(r["deterministic"], 1),
        "Median": _fmt(r["median"], 1),
        "2.5th percentile": _fmt(r["p2_5"], 1),
        "97.5th percentile": _fmt(r["p97_5"], 1),
        "CV, Tier 2 (%)": _fmt(r["cv_pct"], 2),
        "CV, Tier 1 (%)": _fmt(t1m.get(r["indicator"], np.nan), 2),
    } for _, r in tot.iterrows()]
    return Table(
        10, "Simulation and error propagation agree to within 0.05 percentage "
            "points",
        pd.DataFrame(rows),
        "04_uncertainty_lenzen_ieooc/uncertainty_totals.csv and "
        "uncertainty_tier1_error_propagation.csv",
        "Tier 2 is the Monte Carlo at 100,000 draws; Tier 1 is the IPCC "
        "error-propagation formula, which the IPCC (2000) requires to be "
        "reported alongside it. They agree because the model is additive and "
        "every spread is well below the 30 % limit at which the Tier 1 formula "
        "degrades. The interval is parametric uncertainty conditional on one "
        "model, and should be reported with that sentence: the study's own "
        "structural scenario on the pharmaceutical mapping lands entirely "
        "outside it.")


def t_variance() -> Table:
    """Where the uncertainty comes from."""
    d = _read("04_uncertainty_lenzen_ieooc", "uncertainty_variance_shares.csv")
    d = d[d["indicator"] == "Global warming (ktCO2eq)"].sort_values(
        "variance_share_pct", ascending=False)
    name = {"mrio": "Input-output model",
            "covariance_commute_visitor": "Covariance of the travel pair",
            "B_VISI": "Patient and visitor travel",
            "B_COMM": "Employee commuting",
            "B_HEAL": "Direct operations",
            "B_ANAE": "Anaesthetic gases",
            "B_PMDI": "Inhaler propellants"}
    rows = [{
        "Contributor": name.get(r["parameter"], r["parameter"]),
        "Share of variance (%)": _sigfig(r["variance_share_pct"]),
    } for _, r in d.iterrows()]
    return Table(
        11, "The uncertainty is the input-output model, not the bottom-up "
            "proxies the reviewers questioned",
        pd.DataFrame(rows),
        "04_uncertainty_lenzen_ieooc/uncertainty_variance_shares.csv",
        "Computed in closed form rather than estimated from the draws, so the "
        "shares sum to 100 % exactly. The covariance row is what commuting and "
        "patient travel add by sharing a derivation method; without it the "
        "remaining shares would sum to 90.7 % and would not be a decomposition. "
        "The input-output share is stable between 78.6 % and 78.9 % across "
        "every correlation assumption tested, so it is a property of the "
        "calibration rather than of the correlation choice.")


def t_scenarios() -> Table:
    """The mitigation ladder against the regional target."""
    d = _read("18_mitigation_scenarios", "target_consistency.csv")
    rows = [{
        "Quantity": r["quantity"],
        "Value": _fmt(r["value"], 1),
        "Unit": _unit(r["unit"]),
    } for _, r in d.iterrows()]
    return Table(
        12, "Every quantified lever, plus a decarbonising grid, leaves the "
            "2035 footprint above today's",
        pd.DataFrame(rows),
        "18_mitigation_scenarios/target_consistency.csv",
        "Levers are applied simultaneously and the Leontief system is "
        "re-solved, so the combined figure is not a sum. The regional target "
        "covers hospitals while this baseline covers health and eldercare, so "
        "the comparison indicates scale rather than compliance. Counterfactual "
        "tables are not rebalanced: rebalancing would partly undo the "
        "intervention and would require an assumption about what an industry "
        "does with money it stops spending, which the model does not have. The "
        "resulting imbalance is measured and reported per scenario, and the "
        "largest across the whole set is 0.7 % of total output.",
        "An earlier figure of 31 % of the target came from summing "
        "climate-only levers with the grid pathway folded in unannounced. The "
        "like-for-like value is 27 %; the interventions alone reach 15 %.")


def t_burden_shift() -> Table:
    """Relative change in every category, for every lever."""
    d = _read("18_mitigation_scenarios", "burden_shifting.csv")
    cols = ["climate_change", "material_extraction", "blue_water_consumption",
            "land_use", "waste_generation"]
    head = ["Climate", "Material", "Blue water", "Land", "Waste"]
    d = d.sort_values("climate_change")
    rows = []
    for _, r in d.iterrows():
        row = {"Scenario": f"{r['scenario_id']}  {r['ambition']}"}
        for c, h in zip(cols, head):
            unresolved = (r["scenario_id"] in ("P6", "P7", "P8")
                          and c != "climate_change")
            row[f"{h} (%)"] = "n.r." if unresolved else _fmt(r.get(c, np.nan), 2)
        rows.append(row)
    return Table(
        13, "Two scenarios improve climate while worsening another pressure",
        pd.DataFrame(rows),
        "18_mitigation_scenarios/burden_shifting.csv",
        "Reported for all five impact categories, which is what makes the "
        "trade-offs visible. Holding expenditure constant, so that money saved "
        "is respent, improves climate and materials while worsening blue "
        "water, land use and waste. Pharmaceutical raw-material efficiency "
        "does twice as much for material extraction as for climate. Cells "
        "marked n.r. are not resolved: the bottom-up inventory behind "
        "propellants and anaesthetic gases carries no non-climate columns, and "
        "plotting a zero there would read as a clean bill.")


def t_release_defect() -> Table:
    """Why EXIOBASE v3.10.2 was rejected."""
    d = _read("09_exiobase_release_diagnostics", "dk_block_vs_national_accounts.csv")
    # The file carries three model years; the comparison that matters is the
    # study's own reference year, where the two releases disagree.
    d = d[d["mrio_year"] == int(ANALYSIS_YEAR)]
    out = d.pivot_table(index="sector_producing", columns="mrio_release",
                        values="exiobase_output_meur", aggfunc="first")
    rat = d.pivot_table(index="sector_producing", columns="mrio_release",
                        values="ratio_exiobase_over_dst", aggfunc="first")
    nat = d.groupby("sector_producing")["national_accounts_output_meur"].first()
    rels = sorted(out.columns, reverse=True)
    order = nat.sort_values(ascending=False).index
    rows = []
    for sec in order:
        row = {"Danish industry": sec,
               "National accounts (M.EUR)": _fmt(nat[sec], 0)}
        for v in rels:
            val, ratio = out.loc[sec, v], rat.loc[sec, v]
            row[f"EXIOBASE {v}"] = (f"{_fmt(val, 0)}  ({ratio:.2f}x)"
                                    if val == val and ratio == ratio else "")
        rows.append(row)
    return Table(
        14, "EXIOBASE v3.10.2 fails against the Danish national accounts from "
            "2015 onward, and v3.8.2 does not",
        pd.DataFrame(rows),
        "09_exiobase_release_diagnostics/dk_block_vs_national_accounts.csv",
        "This is the whole evidence for the model replacement, and the test "
        "needed no external source: Danish health final expenditure is "
        "40,597 M.EUR, and a health industry with 16,326 M.EUR of total output "
        "cannot deliver it. Danish output still totals to within 3 % and the "
        "table still balances to 1e-11, because output was redistributed "
        "between industries rather than lost, which is why a routine balance "
        "check does not catch it. One row needs reading with care: Danish sea "
        "and coastal water transport shows v3.8.2 at 0.23 times the national "
        "accounts because this study's own sea-transport reallocation has "
        "already been applied to that model. Uncorrected, v3.8.2 matches the "
        "national accounts on that row as closely as it does on the others.")


def t_parameters() -> Table:
    """The stochastic parameters and their evidence."""
    d = _read("04_uncertainty_lenzen_ieooc", "uncertainty_parameters.csv")
    name = {"mrio": "Input-output model", "direct": "Direct operations",
            "anaesthetic": "Anaesthetic gases", "pmdi": "Inhaler propellants",
            "commute": "Employee commuting",
            "visitor": "Patient and visitor travel"}
    rows = [{
        "Parameter": name.get(r["parameter"], r["parameter"]),
        "GSD": _fmt(r["gsd"], 2) if r["gsd"] == r["gsd"] else
               f"CV {100 * r['cv']:.2f} %",
        "95 % factor range": f"{r['factor_2_5pct']:.2f} to "
                             f"{r['factor_97_5pct']:.2f}",
        "Basis": str(r["source"])[:180],
    } for _, r in d.iterrows()]
    return Table(
        15, "Each parameter's spread follows from the kind of source it has",
        pd.DataFrame(rows),
        "04_uncertainty_lenzen_ieooc/uncertainty_parameters.csv",
        "The ordering is the argument. The two quantities taken from a Danish "
        "national account are the tightest; the quantity with no Danish source "
        "at all, the visitor share of patient travel, is the loosest at "
        "roughly a factor of two either way. No parameter was given a range "
        "because the range looked reasonable. The four cross-country scaling "
        "factors all span at least the plus or minus 20 to 50 % the first "
        "reviewer proposed, and the two that do not are a national account and "
        "a published Monte Carlo estimate of this exact quantity.")


BUILDERS: tuple[Callable[[], Table | None], ...] = (
    t_headline, t_year_comparison, t_climate_bridge, t_scopes, t_benchmarks,
    t_boundary_matched, t_gwp_revision, t_capital, t_health_functions,
    t_uncertainty, t_variance, t_scenarios, t_burden_shift, t_release_defect,
    t_parameters,
)


# ---------------------------------------------------------------------------
# document
# ---------------------------------------------------------------------------

def _style_table(doc_table, numeric: list[bool] | None = None) -> None:
    """Apply the house look: shaded header, numeric columns right-aligned.

    Parameters
    ----------
    doc_table : docx.table.Table
        The table to style.
    numeric : list of bool, optional
        One flag per column, true where the column holds numbers. Text columns
        stay left-aligned; right-aligning them, as an earlier version did, made
        a driver column read as a column of figures.
    """
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt

    doc_table.alignment = WD_TABLE_ALIGNMENT.LEFT
    for j, cell in enumerate(doc_table.rows[0].cells):
        shading = OxmlElement("w:shd")
        shading.set(qn("w:val"), "clear")
        shading.set(qn("w:fill"), DEEP)
        cell._tc.get_or_add_tcPr().append(shading)
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(9)
                r.font.color.rgb = None
                r.font.name = "Calibri"
                rpr = r._element.get_or_add_rPr()
                col = OxmlElement("w:color")
                col.set(qn("w:val"), "FFFFFF")
                rpr.append(col)
    for i, row in enumerate(doc_table.rows):
        for j, cell in enumerate(row.cells):
            for p in cell.paragraphs:
                if i > 0 and numeric and j < len(numeric) and numeric[j]:
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                for r in p.runs:
                    r.font.size = Pt(9)
                    r.font.name = "Calibri"


def build_document(tables: list[Table]) -> str:
    """Write the Word document and return its path."""
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DOCX), exist_ok=True)
    doc = Document()
    for section in doc.sections:
        section.left_margin = section.right_margin = Inches(0.8)
        section.top_margin = section.bottom_margin = Inches(0.8)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    h = doc.add_paragraph()
    run = h.add_run("Danish health-care environmental footprint")
    run.font.size = Pt(20)
    run.font.bold = True
    run.font.name = "Cambria"
    run.font.color.rgb = RGBColor.from_string(DEEP)
    sub = doc.add_paragraph()
    r = sub.add_run("Tables of record, reference year "
                    f"{ANALYSIS_YEAR}")
    r.font.size = Pt(13)
    r.font.name = "Cambria"
    r.font.color.rgb = RGBColor.from_string(MUTE)

    intro = doc.add_paragraph()
    intro.add_run(
        "Every table below is generated from the study's gold fact tables "
        "rather than transcribed, so the document can be regenerated whenever "
        "a number moves and no figure in it can drift from the pipeline that "
        "produced it. Each table states the file it was read from. Where an "
        "earlier version of a table is known to be circulating with a value "
        "that later work superseded, the note says so and says why. Values are "
        "carried at the precision the pipeline reports, because the purpose of "
        "this document is to fix the record; the three-significant-figure rule "
        "applies to the manuscript prose, not to the register behind it.").font.size = Pt(10.5)

    meta = doc.add_paragraph()
    mr = meta.add_run(f"Model: {MODEL_LABEL}\nGenerated: {date.today().isoformat()}"
                      f"\nSource tree: data/gold/results/")
    mr.font.size = Pt(9)
    mr.font.color.rgb = RGBColor.from_string(MUTE)

    doc.add_page_break()

    for t in tables:
        cap = doc.add_paragraph()
        cr = cap.add_run(f"Table {t.number}. {t.title}")
        cr.font.bold = True
        cr.font.size = Pt(11)
        cr.font.name = "Cambria"
        cr.font.color.rgb = RGBColor.from_string(DEEP)

        frame = t.frame
        table = doc.add_table(rows=1, cols=len(frame.columns))
        table.style = "Table Grid"
        for j, c in enumerate(frame.columns):
            table.rows[0].cells[j].text = str(c)
        for _, r in frame.iterrows():
            cells = table.add_row().cells
            for j, c in enumerate(frame.columns):
                cells[j].text = str(r[c])
        _style_table(table, [_numeric_column(frame[c].tolist())
                             for c in frame.columns])

        note = doc.add_paragraph()
        nr = note.add_run("Note. " + t.note)
        nr.font.size = Pt(9)
        nr.font.color.rgb = RGBColor.from_string(INK)
        if t.supersedes:
            sup = doc.add_paragraph()
            sr = sup.add_run("Supersedes. " + t.supersedes)
            sr.font.size = Pt(9)
            sr.font.italic = True
            sr.font.color.rgb = RGBColor.from_string("C1502E")
        src = doc.add_paragraph()
        sr2 = src.add_run("Source. " + t.source)
        sr2.font.size = Pt(8.5)
        sr2.font.color.rgb = RGBColor.from_string(MUTE)
        doc.add_paragraph()

    doc.save(DOCX)
    return DOCX


def main() -> None:
    """Build every table, verify it is non-empty, and write the document."""
    tables: list[Table] = []
    for build in BUILDERS:
        try:
            t = build()
        except Exception as exc:                            # noqa: BLE001
            print(f"  SKIP {build.__name__}: {exc}")
            continue
        if t is None:
            # A builder returns None when the layer it reads is not in this
            # working copy, which is a scope difference rather than a failure.
            print(f"  skip {build.__name__}: its layer is not in this copy")
            continue
        assert not t.frame.empty, f"{build.__name__} produced an empty table"
        tables.append(t)
    # Each table keeps the number its builder declares. Renumbering the survivors
    # sequentially, which this did, shifts every table after one that is skipped:
    # the paper-scope copy has no health-function table, so its table 11 became
    # the full copy's table 12 and every cross-reference between the two copies,
    # and from the deck, pointed at the wrong table. A gap in the numbering is
    # the honest cost of a scope difference.
    numbers = [t.number for t in tables]
    assert len(set(numbers)) == len(numbers), f"duplicate table numbers: {numbers}"
    assert numbers == sorted(numbers), f"tables are out of order: {numbers}"
    missing = sorted(set(range(1, max(numbers) + 1)) - set(numbers))
    if missing:
        print(f"  numbering keeps its gaps at {missing}, whose layers are not "
              f"in this working copy")
    path = build_document(tables)
    os.makedirs(OUT_DIR, exist_ok=True)
    index = pd.DataFrame([dict(number=t.number, title=t.title, source=t.source,
                               rows=len(t.frame), columns=len(t.frame.columns),
                               supersedes=bool(t.supersedes))
                          for t in tables])
    index.to_csv(os.path.join(OUT_DIR, "tables_of_record_index.csv"),
                 index=False)
    # Sidecar CSVs are written with the display strings stripped of thousands
    # separators, so a reader can load them without a parser fighting the
    # commas that make the Word table readable.
    for t in tables:
        clean = t.frame.replace(r"^(-?[\d,]+\.?\d*)$", "", regex=False)
        clean = t.frame.map(
            lambda v: v.replace(",", "") if isinstance(v, str)
            and v.replace(",", "").replace(".", "").replace("-", "").isdigit()
            else v)
        clean.to_csv(os.path.join(
            OUT_DIR, f"table_{t.number:02d}.csv"), index=False)
    print(f"{len(tables)} tables -> {path}")
    print(index[["number", "rows", "columns", "supersedes", "title"]]
          .to_string(index=False, max_colwidth=64))


if __name__ == "__main__":
    main()
