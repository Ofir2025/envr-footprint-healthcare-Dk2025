# -*- coding: utf-8 -*-
"""Is the healthcare demand vector nested inside Danish final demand? (No.)

The healthcare final-demand vector y_H is built from Danish national accounts
and then run through EXIOBASE. It is therefore SUPERIMPOSED on the model, not
carved out of EXIOBASE's own Danish final-demand column. This module measures
the gap, because it governs how the headline "share of the national footprint"
may be interpreted.

Denmark 2022 (M.EUR):

  component                    y_H      EXIOBASE DK final demand   ratio
  pharmaceuticals            1,950                       865       2.3x
  medical appliances         1,094                       0.9    1,206x
  healthcare services        8,209 (intermediate inputs) 14,316     0.6x

The appliances result is the striking one: EXIOBASE records essentially NO
Danish final demand for medical precision instruments, while Denmark spends
about EUR 1.1 bn on therapeutic appliances. The same family of Danish
misallocations is documented for water transport by Rormose Jensen & Iliev
(2022, pp. 11-12) and shows up in our own recipe validation.

Consequences, stated plainly for the manuscript:

1. Numerator and denominator are NOT nested. "Healthcare is X % of the Danish
   consumption footprint" compares a nationally-anchored numerator with a
   model-internal denominator that does not fully contain it. This is inherited
   from the Steenmeijer design and is more severe for Denmark than for the
   Netherlands.
2. Shares by product group can therefore exceed 100 % (Chemicals nec 268 %,
   medical instruments far more), which is a diagnostic of the mismatch rather
   than a result.
3. The most defensible denominators are the externally anchored ones -
   Statistics Denmark AFTRYK (62.93 Mt) and Eurostat FIGARO (57.40 Mt) - and
   the share should be reported as a RANGE across denominators, which is what
   the results tables now do.

Run: PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m analysis.demand_vector_consistency
"""

import os
import pickle

import numpy as np
import pandas as pd

from paths import BACKGROUND_DIR, OUTPUT_DIR

NS, NY, K_DK, K_HEALTH, K_CHEM, K_INSTR = 163, 7, 6, 137, 62, 89


def main() -> None:
    """Compare the healthcare demand vector against EXIOBASE's own DK column.

    For pharmaceuticals, medical appliances and healthcare services, computes
    ``y_H`` (the study's superimposed demand, M.EUR) against EXIOBASE's native
    Danish final-demand entry for the mapped sector, and their ratio. Writes
    the table to
    ``data/gold/results/06_benchmarks_validation/demand_vector_consistency.csv``
    and prints it alongside the total Danish final demand EXIOBASE records.
    Reads ``HC_ANALYSIS_YEAR`` from the environment (default ``"2022"``) to
    select the background year's pickled background information.
    """
    year = os.environ.get("HC_ANALYSIS_YEAR", "2022")
    bgy = "2022" if year == "2022" else "2016"
    with open(os.path.join(str(BACKGROUND_DIR),
                           f"gddz_background_information_{bgy}.pkl"), "rb") as fh:
        bg = pickle.load(fh)
    Y, Ys = bg["Y"], bg["Ystim"]
    y_nat = Y[:, K_DK * NY:(K_DK + 1) * NY].sum(axis=1)

    rows = []
    for label, comp, sec, note in (
            ("pharmaceuticals", 2, K_CHEM, "mapped to Chemicals nec"),
            ("medical appliances", 3, K_INSTR, "mapped to Medical precision instruments"),
    ):
        idx = [r * NS + sec for r in range(49)]
        yh, yn = float(Ys[idx, comp].sum()), float(y_nat[idx].sum())
        rows.append(dict(component=label, mapped_sector=note,
                         y_H_meur=yh, exiobase_dk_final_demand_meur=yn,
                         ratio=yh / yn if yn else np.nan))
    h = K_DK * NS + K_HEALTH
    rows.append(dict(component="healthcare services",
                     mapped_sector="scaled intermediate-input column of Health and social work",
                     y_H_meur=float(Ys[:, 1].sum()),
                     exiobase_dk_final_demand_meur=float(y_nat[h]),
                     ratio=float(Ys[:, 1].sum()) / max(float(y_nat[h]), 1e-9)))
    df = pd.DataFrame(rows)
    df["analysis_year"] = year
    df["interpretation"] = (
        "y_H is superimposed on the model rather than carved out of EXIOBASE's "
        "Danish final demand; numerator and denominator are not nested, so the "
        "share of the national footprint must be read as a comparison across "
        "denominators, not as a partition")
    out_dir = os.path.join(str(OUTPUT_DIR), "06_benchmarks_validation")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "demand_vector_consistency.csv")
    df.to_csv(out, index=False)
    print(df[["component", "y_H_meur", "exiobase_dk_final_demand_meur", "ratio"]]
          .round(1).to_string(index=False))
    print(f"\nTotal Danish final demand in EXIOBASE: {y_nat.sum():,.0f} M.EUR")
    print(f"written -> {out}")


if __name__ == "__main__":
    main()
