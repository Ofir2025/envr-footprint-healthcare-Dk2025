# -*- coding: utf-8 -*-
"""Monte Carlo uncertainty and scenario analysis for the Danish healthcare footprint.

Responds to the first-round reviews (systematic uncertainty on the bottom-up
scaling factors and proxies; sensitivity of the pharmaceuticals-to-Chemicals-nec
mapping; the 2019-expenditure-on-2016-price-model mismatch; effect on
contribution rankings).

Design (see docs/revision/uncertainty_design_notes.md for the literature basis):

* The footprint is linear in final demand and the bottom-up items are additive,
  so no perturbation of the Leontief system is required: each draw recombines
  precomputed components. EXIOBASE publishes no element-level standard
  deviations, so MRIO-parameter propagation (Eora/Lenzen-style) is impossible
  by construction and is addressed qualitatively; the literature indicates
  IO-parameter noise adds little relative uncertainty compared with the terms
  propagated here (Perkins & Suh 2019; Jakobs 2023).
* Stochastic parameters are sampled independently as lognormals with median 1
  at the central estimate (right-skewed multiplicative uncertainty, standard in
  hybrid-LCA practice; GSDs below). Structural choices are discrete scenarios.
* 10,000 draws (convergence precedent: Jakobs 2023, ch. 3), fixed seed.

Inputs: the corrected model outputs in data/gold/results (table_1.xlsx and
contribution_analysis.xlsx). Run AFTER analysis.main_2025:

    PYTHONPATH=src python -m analysis.uncertainty_2025
"""

import numpy as np
import pandas as pd
import os

from paths import OUTPUT_DIR

N_DRAWS = 10_000
SEED = 42

# --------------------------------------------------------------------------
# Parameter distributions (median, geometric standard deviation) and rationale
# --------------------------------------------------------------------------
# GSD 1.25 ~ 95% range (-36%, +56%): inside the reviewers' +/-20-50% band.
PARAMS = {
    # bottom-up items (multiplicative on the item's full row)
    "anaesthetic": {"gsd": 1.30, "why": "NID 2.G.3.a activity +/-25%, EF +/-20% (DCE 2024); volatile component is a population-scaled proxy"},
    "pmdi":        {"gsd": 1.15, "why": "register-based dispensing (medstat.dk) x producer HFC content; GWP-metric and per-dose spread"},
    "commute":     {"gsd": 1.25, "why": "ratio method: NL base values + DK/NL employment, hours, TU distance"},
    "visitor":     {"gsd": 1.40, "why": "no Danish primary source; Dutch base is itself a transplanted English per-capita figure"},
    # direct operational emissions (DRIVHUS-based)
    "direct":      {"gsd": 1.10, "why": "official emission accounts; alpha-proration of industry 880000 and medical-N2O netting"},
    # MRIO-side multiplicative factors
    "deflator":    {"median": 0.966, "gsd": 1.02,
                    "why": "2019 expenditure on a 2016-price table: Danish net price index 2016->2019 ~ +3.5%; sampled around the deflated level"},
    "waste_ext":   {"gsd": 1.50, "why": "waste extension = 2011 hybrid-EXIOBASE absolute account on 2016 monetary output (Steenmeijer precedent); vintage+classification mismatch"},
}

# Pharma-mapping scenario B: pharma-specific intensity relative to Chemicals nec.
# Climate ~1/3 and materials ~1/7 per the Dutch SNAC-based evidence cited by
# Steenmeijer et al. (2022, discussion); wide GSD per the within-sector
# heterogeneity literature (Majeau-Bettez et al. 2011; Yang et al. 2017).
PHARMA_RATIO = {
    "Global warming (ktCO2eq)":     {"median": 1/3, "gsd": 1.5},
    "Material extraction (kt)":     {"median": 1/7, "gsd": 1.5},
    # no pharma-specific evidence for the remaining categories: uniform between
    # the strongest documented reduction and no reduction
    "Blue water consumption (Mm3)": {"uniform": (1/7, 1.0)},
    "Land use (km2)":               {"uniform": (1/7, 1.0)},
    "Waste generation (kt)":        {"uniform": (1/7, 1.0)},
}

INDICATORS = [
    "Global warming (ktCO2eq)",
    "Material extraction (kt)",
    "Blue water consumption (Mm3)",
    "Land use (km2)",
    "Waste generation (kt)",
]


def _lognormal(rng, median, gsd, n):
    return rng.lognormal(mean=np.log(median), sigma=np.log(gsd), size=n)


def load_components():
    """Additive components per indicator from the corrected model outputs."""
    t1 = pd.read_excel(os.path.join(OUTPUT_DIR, "table_1.xlsx"), index_col=0)
    full = pd.read_excel(os.path.join(OUTPUT_DIR, "contribution_analysis.xlsx"),
                         sheet_name="full", index_col=0)
    b_heal = full[full["SecTxtCode"] == "B_HEAL"][INDICATORS].astype(float).sum()

    comp = pd.DataFrame({
        # MRIO components (direct row is inside 'Healthcare services' in table 1)
        "hc_mrio":  t1.loc["Healthcare services", INDICATORS].astype(float) - b_heal,
        "pharma":   t1.loc["Pharmaceuticals and chemical products", INDICATORS].astype(float),
        "appl":     t1.loc["Medical appliances", INDICATORS].astype(float),
        "direct":   b_heal,
        "anaesthetic": t1.loc["Release of anaesthetic gases", INDICATORS].astype(float),
        "pmdi":     t1.loc["Release of pMDI propellants", INDICATORS].astype(float),
        "travel":   t1.loc["Private travel", INDICATORS].astype(float),
    })
    # split travel into commute/visitor with the shares of the underlying file
    bu = pd.read_csv(os.path.join(os.path.dirname(str(OUTPUT_DIR)), "..", "silver",
                                  "inputs", "dk_bottomup_data_2025.txt"), sep="\t"
                     ).set_index("Source")
    c = bu.loc["Commute (total)", "Global warming (ktCO2eq)"]
    v = bu.loc["Visitor travel (total)", "Global warming (ktCO2eq)"]
    share_commute = float(c) / float(c + v)
    comp["commute"] = comp["travel"] * share_commute
    comp["visitor"] = comp["travel"] * (1 - share_commute)
    comp = comp.drop(columns=["travel"])
    return comp


def run_mc(comp, pharma_scenario="A", n=N_DRAWS, seed=SEED):
    rng = np.random.default_rng(seed)
    draws = {
        "anaesthetic": _lognormal(rng, 1.0, PARAMS["anaesthetic"]["gsd"], n),
        "pmdi":        _lognormal(rng, 1.0, PARAMS["pmdi"]["gsd"], n),
        "commute":     _lognormal(rng, 1.0, PARAMS["commute"]["gsd"], n),
        "visitor":     _lognormal(rng, 1.0, PARAMS["visitor"]["gsd"], n),
        "direct":      _lognormal(rng, 1.0, PARAMS["direct"]["gsd"], n),
        "deflator":    _lognormal(rng, PARAMS["deflator"]["median"], PARAMS["deflator"]["gsd"], n),
        "waste_ext":   _lognormal(rng, 1.0, PARAMS["waste_ext"]["gsd"], n),
    }
    ratios = {}
    for k in INDICATORS:
        spec = PHARMA_RATIO[k]
        if pharma_scenario == "A":
            ratios[k] = np.ones(n)
        elif "uniform" in spec:
            lo, hi = spec["uniform"]
            ratios[k] = rng.uniform(lo, hi, n)
        else:
            ratios[k] = np.clip(_lognormal(rng, spec["median"], spec["gsd"], n), None, 1.0)

    totals = {}
    for k in INDICATORS:
        c = comp.loc[k]
        mrio = (c["hc_mrio"] + c["appl"] + c["pharma"] * ratios[k]) * draws["deflator"]
        if k == "Waste generation (kt)":
            mrio = mrio * draws["waste_ext"]
        tot = (mrio
               + c["direct"] * draws["direct"]
               + c["anaesthetic"] * draws["anaesthetic"]
               + c["pmdi"] * draws["pmdi"]
               + c["commute"] * draws["commute"]
               + c["visitor"] * draws["visitor"])
        totals[k] = tot
    return totals, draws, ratios


def summarize(totals):
    rows = []
    for k, arr in totals.items():
        q = np.percentile(arr, [2.5, 16, 50, 84, 97.5])
        rows.append({"indicator": k, "p2.5": q[0], "p16": q[1], "median": q[2],
                     "p84": q[3], "p97.5": q[4],
                     "rel_low_%": 100 * (q[0] / q[2] - 1),
                     "rel_high_%": 100 * (q[4] / q[2] - 1)})
    return pd.DataFrame(rows)


def tornado(comp, pharma_scenario="A"):
    """One-at-a-time swings at each parameter's 2.5/97.5 percentile (GWP only)."""
    k = "Global warming (ktCO2eq)"
    c = comp.loc[k]
    base_ratio = 1.0 if pharma_scenario == "A" else PHARMA_RATIO[k]["median"]
    defl = PARAMS["deflator"]["median"]

    def total(**over):
        p = {"anaesthetic": 1, "pmdi": 1, "commute": 1, "visitor": 1, "direct": 1,
             "deflator": defl, "ratio": base_ratio}
        p.update(over)
        mrio = (c["hc_mrio"] + c["appl"] + c["pharma"] * p["ratio"]) * p["deflator"]
        return (mrio + c["direct"] * p["direct"] + c["anaesthetic"] * p["anaesthetic"]
                + c["pmdi"] * p["pmdi"] + c["commute"] * p["commute"]
                + c["visitor"] * p["visitor"])

    base = total()
    rows = []
    z = 1.959964
    for name in ["anaesthetic", "pmdi", "commute", "visitor", "direct"]:
        gsd = PARAMS[name]["gsd"]
        lo, hi = gsd ** -z, gsd ** z
        rows.append({"parameter": name, "low": total(**{name: lo}) - base,
                     "high": total(**{name: hi}) - base})
    gsd = PARAMS["deflator"]["gsd"]
    rows.append({"parameter": "deflator",
                 "low": total(deflator=defl * gsd ** -z) - base,
                 "high": total(deflator=defl * gsd ** z) - base})
    if pharma_scenario == "B":
        gsd = PHARMA_RATIO[k]["gsd"]
        rows.append({"parameter": "pharma_ratio",
                     "low": total(ratio=min(base_ratio * gsd ** -z, 1.0)) - base,
                     "high": total(ratio=min(base_ratio * gsd ** z, 1.0)) - base})
    # reviewer-verbatim swings
    for pct in (0.2, 0.5):
        for name in ["anaesthetic", "pmdi", "commute", "visitor"]:
            rows.append({"parameter": f"{name} +/-{int(pct*100)}%",
                         "low": total(**{name: 1 - pct}) - base,
                         "high": total(**{name: 1 + pct}) - base})
    df = pd.DataFrame(rows)
    df["base_total"] = base
    return df.sort_values("high", key=lambda s: s.abs(), ascending=False)


def ranking_probabilities(pharma_scenario, comp, n=N_DRAWS, seed=SEED):
    """Probability that each contribution group holds each rank (per indicator).

    Groups are the Figure-1 aggregation. The pharma-ratio scenario is applied to
    the 'Pharmaceuticals and chemical products' group via the pharma demand
    component (an approximation: most of that component's footprint lands in
    that group); bottom-up multipliers apply to their groups.
    """
    fig1 = pd.read_excel(os.path.join(OUTPUT_DIR, "full_results_tables.xlsx"),
                         sheet_name="Fig1_absolute", index_col=0)
    rng = np.random.default_rng(seed + 1)
    out = {}
    for k in INDICATORS:
        g = fig1[k].astype(float).copy()
        n_groups = len(g)
        draws = np.tile(g.values, (n, 1))
        idx = {name: i for i, name in enumerate(g.index)}
        spec = PHARMA_RATIO[k]
        if pharma_scenario == "A":
            ratio = np.ones(n)
        elif "uniform" in spec:
            ratio = rng.uniform(*spec["uniform"], n)
        else:
            ratio = np.clip(_lognormal(rng, spec["median"], spec["gsd"], n), None, 1.0)
        pharma_component = comp.loc[k, "pharma"]
        if "Pharmaceuticals and chemical products" in idx:
            draws[:, idx["Pharmaceuticals and chemical products"]] -= (1 - ratio) * pharma_component
        if "Individual travel" in idx:
            f = (_lognormal(rng, 1, PARAMS["commute"]["gsd"], n)
                 + _lognormal(rng, 1, PARAMS["visitor"]["gsd"], n)) / 2
            draws[:, idx["Individual travel"]] *= f
        if "Operational impacts" in idx:
            draws[:, idx["Operational impacts"]] *= _lognormal(rng, 1, PARAMS["direct"]["gsd"], n)
        ranks = (-draws).argsort(axis=1).argsort(axis=1)  # 0 = largest
        prob = pd.DataFrame(
            {f"P(rank {r+1})": (ranks == r).mean(axis=0) for r in range(min(3, n_groups))},
            index=g.index,
        )
        out[k] = prob.sort_values("P(rank 1)", ascending=False)
    return out


def main():
    comp = load_components()  # indicators as rows, components as columns
    writer_path = os.path.join(OUTPUT_DIR, "uncertainty_summary.xlsx")
    with pd.ExcelWriter(writer_path, engine="xlsxwriter") as xw:
        comp.to_excel(xw, sheet_name="components")
        for scen in ("A", "B"):
            totals, _, _ = run_mc(comp, pharma_scenario=scen)
            summarize(totals).to_excel(xw, sheet_name=f"totals_scenario_{scen}", index=False)
            tornado(comp, pharma_scenario=scen).to_excel(
                xw, sheet_name=f"tornado_{scen}", index=False)
            probs = ranking_probabilities(scen, comp)
            startrow = 0
            for k, df in probs.items():
                df.insert(0, "indicator", k)
                df.to_excel(xw, sheet_name=f"rankings_{scen}", startrow=startrow)
                startrow += len(df) + 3
        pd.DataFrame([
            {"parameter": name, **{kk: vv for kk, vv in spec.items()}}
            for name, spec in PARAMS.items()
        ]).to_excel(xw, sheet_name="parameters", index=False)
    print(f"Uncertainty summary written -> {writer_path}")
    for scen in ("A", "B"):
        totals, _, _ = run_mc(comp, pharma_scenario=scen)
        s = summarize(totals)
        print(f"\nScenario {scen} (pharma mapping {'as Chemicals nec' if scen=='A' else 'pharma-specific intensity'}):")
        print(s.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
