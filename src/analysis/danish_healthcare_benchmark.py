# -*- coding: utf-8 -*-
"""Benchmark the Danish health-care footprint against the published comparator.

Schmidt & Merciai (2023), *GHG emissions from Danish consumption 2016*, report a
Danish national consumption footprint of 73.9 Mt CO2-e (12.9 t per capita) on
the EXIOBASE v4 hybrid model, and within it **"Health and social work services"
at 6.1 Mt CO2-e, 1.07 t per capita, 8.3 % of the national total**. It is the only
published Danish health-sector footprint on an EXIOBASE-family model, and
therefore the closest available comparator for this study.

Comparing headline to headline would mislead. Three boundary differences must be
removed first, and each is documented and reversible here:

1. **Sector boundary.** Their "Health and social work services" is the whole of
   NACE Q - human health, residential care and social work *including
   childcare*. This study's default is health plus eldercare, excluding
   childcare. The comparable run is ``HC_SCOPE=zorg_en_welzijn``.
2. **Capital.** They endogenise fixed capital, which contributes 1.1 t per
   capita to their national total. This study excludes it from the headline. The
   comparable figure applies the endogenisation uplift measured in
   :mod:`analysis.capital_gfcf`.
3. **Model type.** Theirs is *consequential* (marginal), ours *attributional*.
   This cannot be reconciled by adjustment and is stated as a residual caveat
   rather than corrected away.

Run
---
``PYTHONPATH=src .venv/bin/python -m analysis.danish_healthcare_benchmark``
"""

from __future__ import annotations

import os
from typing import Any

import pandas as pd

from analysis.constants import ANALYSIS_YEAR, DK_POPULATION, MODEL_LABEL, eriksen_folder
from paths import OUTPUT_DIR

FOLDER = "06_benchmarks_validation"

#: Schmidt & Merciai (2023), 2.-0 LCA consultants for CONCITO. Danish
#: consumption-based GHG emissions 2016, EXIOBASE v4 hybrid, consequential.
SCHMIDT_MERCIAI: dict[str, Any] = {
    "source": "Schmidt & Merciai 2023, GHG emissions from Danish consumption 2016",
    "year": 2016,
    "model": "EXIOBASE v4 hybrid, consequential, fixed capital endogenised",
    "national_mt": 73.9,
    "national_t_per_capita": 12.9,
    "health_sector_label": "Health and social work services (NACE Q, incl. childcare)",
    "health_mt": 6.1,
    "health_t_per_capita": 1.07,
    "health_share_of_national_pct": 8.3,
    "capital_contribution_t_per_capita": 1.1,
}


def _scope_total(scope: str) -> float:
    """Read one boundary scenario's grand total, in kt CO2-equivalent.

    Parameters
    ----------
    scope : str
        ``"health_only"``, ``"health_eldercare"`` or ``"zorg_en_welzijn"``.

    Returns
    -------
    float
        Grand total in kt CO2-equivalent.

    Raises
    ------
    FileNotFoundError
        If the scenario has not been generated, rather than falling back to a
        stale or default value.
    """
    folder = eriksen_folder() if scope == "health_eldercare" \
        else os.path.join("scenarios", scope)
    path = os.path.join(str(OUTPUT_DIR), folder, "scopes_summary.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"scenario {scope!r} not generated; run "
            f"HC_SCOPE={scope} python -m analysis.main_2025")
    frame = pd.read_csv(path).set_index("Component")["kt_CO2eq"]
    return float(frame["Grand Total"])


def _capital_uplift() -> float:
    """Ratio of the fully endogenised capital scenario to the baseline."""
    path = os.path.join(str(OUTPUT_DIR), "11_capital_gfcf",
                        "capital_scenarios_by_indicator.csv")
    frame = pd.read_csv(path)
    climate = frame[frame.indicator == "climate_change"].set_index("scenario")
    return float(climate.loc["D_full_endogenisation", "value"]
                 / climate.loc["baseline_capital_excluded", "value"])


def main() -> None:
    """Build the boundary-matched comparison and write it to the gold folder."""
    out_dir = os.path.join(str(OUTPUT_DIR), FOLDER)
    os.makedirs(out_dir, exist_ok=True)
    population = DK_POPULATION[ANALYSIS_YEAR]
    uplift = _capital_uplift()

    def per_capita(kt: float) -> float:
        """Convert a kt CO2-equivalent total to kg CO2-equivalent per capita.

        Parameters
        ----------
        kt : float
            Total in kt CO2-equivalent.

        Returns
        -------
        float
            Per-capita footprint in kg CO2-equivalent, dividing by the
            closed-over ``population`` for ``ANALYSIS_YEAR``.
        """
        return kt * 1e3 / population

    default = _scope_total("health_eldercare")
    nace_q = _scope_total("zorg_en_welzijn")
    matched = nace_q * uplift

    national = pd.read_csv(os.path.join(
        str(OUTPUT_DIR), "00_core_footprint", "national_totals_summary.csv"))
    national_kt = float(national.loc[national.indicator == "climate_change",
                                     "national_footprint"].iloc[0])

    rows: list[dict[str, Any]] = [
        dict(basis="Schmidt & Merciai 2023 (published comparator)",
             sector_boundary=SCHMIDT_MERCIAI["health_sector_label"],
             capital="endogenised", model_type="consequential",
             year=SCHMIDT_MERCIAI["year"],
             value_kt=SCHMIDT_MERCIAI["health_mt"] * 1e3,
             t_per_capita=SCHMIDT_MERCIAI["health_t_per_capita"],
             share_of_national_pct=SCHMIDT_MERCIAI["health_share_of_national_pct"],
             comparable_with_published=True),
        dict(basis="this study, headline", sector_boundary="health + eldercare",
             capital="excluded", model_type="attributional",
             year=int(ANALYSIS_YEAR), value_kt=default,
             t_per_capita=per_capita(default),
             share_of_national_pct=100 * default / national_kt,
             comparable_with_published=False),
        dict(basis="this study, sector boundary matched",
             sector_boundary="NACE Q incl. childcare (HC_SCOPE=zorg_en_welzijn)",
             capital="excluded", model_type="attributional",
             year=int(ANALYSIS_YEAR), value_kt=nace_q,
             t_per_capita=per_capita(nace_q),
             share_of_national_pct=100 * nace_q / national_kt,
             comparable_with_published=False),
        dict(basis="this study, sector boundary AND capital matched",
             sector_boundary="NACE Q incl. childcare",
             capital=f"endogenised (uplift {uplift:.4f} from analysis.capital_gfcf)",
             model_type="attributional", year=int(ANALYSIS_YEAR),
             value_kt=matched, t_per_capita=per_capita(matched),
             share_of_national_pct=100 * matched / national_kt,
             comparable_with_published=True),
    ]
    table = pd.DataFrame(rows)
    table["ratio_to_published"] = (table["t_per_capita"]
                                   / SCHMIDT_MERCIAI["health_t_per_capita"])
    table["model"] = MODEL_LABEL
    table["residual_caveat"] = (
        "their model is consequential (marginal), ours attributional; that "
        "difference cannot be removed by boundary adjustment and remains")
    table.to_csv(os.path.join(
        out_dir, "danish_healthcare_benchmark_boundary_matched.csv"),
        index=False)

    pd.set_option("display.width", 200)
    print(table[["basis", "value_kt", "t_per_capita",
                 "share_of_national_pct", "ratio_to_published"]]
          .round(3).to_string(index=False, max_colwidth=48))
    print(f"\nBoundary-matched agreement: "
          f"{table['ratio_to_published'].iloc[-1]:.3f} of the published "
          f"per-capita value; national share "
          f"{table['share_of_national_pct'].iloc[-1]:.1f} % against their "
          f"{SCHMIDT_MERCIAI['health_share_of_national_pct']} %")
    print(f"\nwritten -> {out_dir}")


if __name__ == "__main__":
    main()
