# -*- coding: utf-8 -*-
"""Build the pickled EE-MRIO background for 2022 from EXIOBASE v3.10.2.

EXIOBASE restructured its distribution from v3.9/v3.10: the archive root holds
Z.txt, Y.txt, x.txt and unit.txt, and the satellite accounts are split into
per-domain folders (air_emissions, energy, employment, factor_inputs, land,
material, nutrients, water), each with F.txt / F_Y.txt / unit.txt. This builder
produces pickles with exactly the structure `analysis.functions_2025.
createBackground` expects, written under version-tagged names
(mrio2022_v3_10_2.pkl incl. Z and x, leontief2022_v3_10_2.pkl) so they cannot
overwrite the v3.8.2 background the study's published numbers rest on.

Design decisions (documented for the methods section):
* A is derived as Z x̂⁻¹ from the official Z and x files (v3.7-era releases
  shipped A directly; v3.10.2 ships Z and x).
* Labels are REUSED from the 2016 background (exio2016.pkl) after hard
  assertions that the v3.10.2 region and industry orderings are identical -
  EXIOBASE's 49-region/163-industry ordering is stable across v3.x, and the
  assertion turns any silent change into a loud failure.
* The characterisation matrix Q (6 x n_stressors) is rebuilt by NAME-matching
  the stressor names of the 2016 background's Q (the Steenmeijer/DESIRE
  selection: GWP100 with CH4=25/N2O=298, abiotic Domestic Extraction Used,
  blue water consumption, land use, value added, employment) onto the stacked
  v3.10.2 stressor list. Every unmatched name is reported; the build fails if
  any GWP-carrying name is lost.
* The waste extension row is the 2011 hybrid-EXIOBASE waste account prepared
  by the canonical waste stage (waste.pkl); region/industry layout is identical
  (asserted), so it is reused as-is - the same Steenmeijer-precedent reference-
  year carry-forward as in the 2016 model, treated in the uncertainty analysis.

Run:  PYTHONPATH=src .venv/bin/python -m pipelines.prep_background_2022.build_background_2022
"""

import os
import pickle
import time

import numpy as np
import pandas as pd

from paths import MRIO_DIR

YEAR = "2022"
VERSION_TAG = "_v3_10_2"   # see the write block: the tag prevents a silent
                           # overwrite of the v3.8.2 background the study uses
V3102_DIR = (
    "/Users/kwametutu/Library/CloudStorage/OneDrive-Personal/Data/lca/input_output/"
    "mrio/exiobase/versions/v3_10_2/txt"
)
SATELLITE_DOMAINS = [
    "factor_inputs",   # first, so the 9 primary-input rows lead (v3.7 convention)
    "employment",
    "air_emissions",
    "energy",
    "land",
    "material",
    "nutrients",
    "water",
]


def main():
    t0 = time.time()
    mrio_dir = str(MRIO_DIR) + os.sep

    with open(mrio_dir + "exio2016.pkl", "rb") as fh:
        ref = pickle.load(fh)
    ref_label = ref["label"]
    ref_ext_names = [str(x) for x in ref_label["extension"]["Name"]]
    ref_Q = ref["Q"]

    # ---- economic core -----------------------------------------------------
    print("reading unit.txt / Y / x ...")
    unit = pd.read_csv(os.path.join(V3102_DIR, "unit.txt"), sep="\t", index_col=[0, 1])
    regions_seq = [unit.index[i * 163][0] for i in range(len(unit) // 163)]
    industries_seq = [unit.index[i][1] for i in range(163)]

    assert list(ref_label["region"].index) == regions_seq, "v3.10.2 region order differs from 2016 background"
    assert list(ref_label["industry"]["Name"]) == industries_seq, "v3.10.2 industry order differs from 2016 background"

    Y = np.array(pd.read_csv(os.path.join(V3102_DIR, "Y.txt"), sep="\t", index_col=[0, 1], header=[0, 1]))
    x = np.array(pd.read_csv(os.path.join(V3102_DIR, "x.txt"), sep="\t", index_col=[0, 1])).reshape(-1, 1)

    print("reading Z.txt (large) ...")
    Z = np.array(pd.read_csv(os.path.join(V3102_DIR, "Z.txt"), sep="\t", index_col=[0, 1], header=[0, 1]))
    n = Z.shape[0]
    assert n == 49 * 163 and Y.shape == (n, 49 * 7)

    xinv = np.where(x[:, 0] != 0, 1.0 / np.where(x[:, 0] != 0, x[:, 0], 1.0), 0.0)
    A = Z * xinv[np.newaxis, :]

    print("inverting (I - A) ...")
    L = np.linalg.inv(np.eye(n) - A)

    # ---- satellites --------------------------------------------------------
    F_blocks, FY_blocks, names, units = [], [], [], []
    for dom in SATELLITE_DOMAINS:
        d = os.path.join(V3102_DIR, dom)
        f = pd.read_csv(os.path.join(d, "F.txt"), sep="\t", index_col=[0], header=[0, 1])
        fy = pd.read_csv(os.path.join(d, "F_Y.txt"), sep="\t", index_col=[0], header=[0, 1])
        u = pd.read_csv(os.path.join(d, "unit.txt"), sep="\t", index_col=[0])
        assert list(f.index) == list(fy.index)
        # v3.10.2 leaves cells empty where an account has no entry -> treat as 0
        F_blocks.append(np.nan_to_num(np.array(f), nan=0.0))
        FY_blocks.append(np.nan_to_num(np.array(fy), nan=0.0))
        names.extend([str(i) for i in f.index])
        units.extend([str(u.loc[i].iloc[0]) if i in u.index else "" for i in f.index])
        print(f"  {dom:14s} {f.shape[0]:4d} stressors")
    R = np.vstack(F_blocks)
    H = np.vstack(FY_blocks)

    n_pri = 9  # taxes/subsidies/compensation/surplus rows of factor_inputs
    V = R[:n_pri, :]

    # ---- multiplier-outlier screening (Statistics Denmark remedy) ----------
    # EXIOBASE's environmental accounts are compiled independently of the
    # monetary core, so industries with (near-)zero output can carry finite
    # emissions, producing absurd intensities (documented for Denmark's coupled
    # model by Rormose Jensen & Iliev 2022, Table 2 and pp. 18-20; observed
    # here e.g. GB medical-instruments at 2e8 kt CO2e/MEUR). Instead of their
    # admittedly arbitrary absolute cap we implement their proposed second-best:
    # for every stressor x sector, intensities more than OUTLIER_FACTOR times
    # the cross-region median intensity (computed over regions with output
    # above DE_MINIMIS_MEUR), and all entries on below-de-minimis outputs, are
    # replaced by the median intensity times the node's actual output.
    # Screening applies ONLY to the air-emissions rows: emission accounts are
    # compiled independently of the monetary core (the DST-documented failure
    # mode), whereas extraction/land/water accounts are legitimately
    # concentrated in few region-sectors - a cross-region median test would
    # wrongly crush real mines and irrigated agriculture (cf. the concentrated-
    # stressor caution in Jakobs 2023, ch. 3).
    air_start = 9 + 12                      # after factor_inputs + employment
    air_stop = air_start + 420              # air_emissions block
    DE_MINIMIS_MEUR = 1.0
    OUTLIER_FACTOR = 100.0
    xs = x[:, 0].reshape(49, 163)
    n_repl_total, mass_moved = 0, 0.0
    for r in range(air_start, air_stop):
        Rr = R[r, :].reshape(49, 163)
        with np.errstate(divide="ignore", invalid="ignore"):
            inten = np.where(xs > 0, Rr / np.where(xs > 0, xs, 1.0), 0.0)
        valid = xs > DE_MINIMIS_MEUR
        med = np.zeros(163)
        for s in range(163):
            v = inten[valid[:, s], s]
            v = v[v > 0]
            med[s] = np.median(v) if v.size else 0.0
        bad = (~valid & (Rr > 0)) | (valid & (inten > OUTLIER_FACTOR * np.maximum(med, 1e-300))[:, :] & (med > 0)[np.newaxis, :])
        if bad.any():
            repl = med[np.newaxis, :] * xs
            mass_moved += float(np.abs(Rr[bad] - repl[bad]).sum())
            n_repl_total += int(bad.sum())
            Rr[bad] = repl[bad]
            R[r, :] = Rr.reshape(-1)
    print(f"  outlier screening: {n_repl_total} stressor-node entries replaced by "
          f"cross-region median intensity (factor>{OUTLIER_FACTOR:g} or output<{DE_MINIMIS_MEUR:g} MEUR)")

    # ---- characterisation by name matching --------------------------------
    Q = np.zeros((ref_Q.shape[0], R.shape[0]))
    name_pos = {}
    for i, nm in enumerate(names):
        name_pos.setdefault(nm, i)
    report = []
    for row in range(ref_Q.shape[0]):
        src = np.where(ref_Q[row] != 0)[0]
        matched = missed = 0
        missed_names = []
        for j in src:
            nm = ref_ext_names[j]
            if nm in name_pos:
                Q[row, name_pos[nm]] = ref_Q[row, j]
                matched += 1
            else:
                missed += 1
                missed_names.append(nm)
        report.append((row, matched, missed, missed_names))
        print(f"  Q row {row} ({ref_label['characterization']['Name'].iloc[row]}): "
              f"{matched} matched, {missed} missed" + (f" -> {missed_names[:5]}" if missed_names else ""))
    assert report[0][2] == 0, f"GWP stressors unmatched in v3.10.2: {report[0][3]}"

    # v3.10.2 restructured three satellite families; rebuild those rows from the
    # new names with the SAME concept definitions (all characterisation factors 1):
    #  - abiotic material extraction = Domestic Extraction Used, metal ores +
    #    non-metallic minerals (Steenmeijer et al. SI S4.2);
    #  - land use = all land-account rows (artificial surfaces, cropland incl.
    #    fallowed, forest, permanent pastures) - v3.7's "Other land Use: Total"
    #    category no longer exists;
    #  - employment = the six "Employment people" rows (head counts, not hours).
    def _rebuild_row(row, predicate, what):
        Q[row, :] = 0.0
        hits = [i for i, nm in enumerate(names) if predicate(nm)]
        Q[row, hits] = 1.0
        print(f"  Q row {row} rebuilt from v3.10.2 names ({what}): {len(hits)} stressors")

    _rebuild_row(1, lambda nm: nm.startswith("Domestic Extraction Used - Metal Ores -")
                 or nm.startswith("Domestic Extraction Used - Non-Metallic Minerals -"),
                 "abiotic DEU: metal ores + non-metallic minerals")
    land_names = set()
    with open(os.path.join(V3102_DIR, "land", "unit.txt")) as fh:
        next(fh)
        for line in fh:
            land_names.add(line.split("\t")[0].strip())
    _rebuild_row(3, lambda nm: nm in land_names, "all land accounts")
    _rebuild_row(5, lambda nm: nm.startswith("Employment people:"), "employment head counts")

    # ---- labels ------------------------------------------------------------
    label = {
        "region": ref_label["region"].copy(),
        "industry": ref_label["industry"].copy(),
        "final": ref_label["final"].copy(),
        "primary": ref_label["primary"].copy(),
        "extension": pd.DataFrame({"Name": names, "unit": units}),
        "characterization": ref_label["characterization"].iloc[: ref_Q.shape[0]].copy(),
    }

    mrio = {"Y": Y, "A": A, "V": V, "R": R, "H": H, "Q": Q, "label": label,
            "Z": Z, "x": x,
            "source": "EXIOBASE v3.10.2 (Zenodo 20051562) IOT_2022_ixi, official txt distribution"}

    # Version-tagged filenames, and the tag is not optional.
    #
    # This builder reads v3.10.2. `pipelines.prep_background_2025` reads v3.8.2,
    # which is the release the study uses and the one every published number
    # rests on. Both used to write `mrio2022.pkl` and `leontief2022.pkl`, so
    # running this module overwrote the headline background in place - and
    # nothing downstream could notice, because `constants.model_label()` stamps
    # "EXIOBASE v3.8.2" from a constant rather than from the pickle. Audit check
    # C4 would have passed on tables built from the rejected release.
    #
    # The hand-made `mrio2022_v3_10_2.pkl` on disk is the evidence that this
    # already happened once and was repaired by hand. Writing the tag natively
    # makes the collision impossible rather than merely unlikely, and lets the
    # two releases coexist - which layer 09 needs, since its whole purpose is to
    # compare them.
    with open(mrio_dir + f"mrio{YEAR}{VERSION_TAG}.pkl", "wb") as fh:
        pickle.dump(mrio, fh)
    with open(mrio_dir + f"leontief{YEAR}{VERSION_TAG}.pkl", "wb") as fh:
        pickle.dump(L, fh)

    # waste layout check (region/industry ordering identical -> reusable)
    with open(mrio_dir + "waste.pkl", "rb") as fh:
        waste = pickle.load(fh)
    assert waste["r"].shape[1] == n and waste["h"].shape[1] == Y.shape[1]

    print(f"done in {time.time() - t0:5.1f} s -> mrio{YEAR}.pkl, leontief{YEAR}.pkl (waste.pkl reused)")


if __name__ == "__main__":
    main()
