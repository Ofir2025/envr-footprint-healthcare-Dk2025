# -*- coding: utf-8 -*-
"""Main analysis: the Danish health-care environmental footprint.

Orchestrates the whole calculation - expenditure vector, background EE-MRIO,
Leontief solution, bottom-up additions, scope split, and the output tables and
figures. Parameterised by ``HC_ANALYSIS_YEAR``, ``HC_BACKGROUND_TAG`` and
``HC_SCOPE`` (see ``docs/README.md``).

Run::

    HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \\
        python -m analysis.main_2025

Script for:
'The environmental impacts of the Danish health care system: supply-chain origins and geographical displacement of impacts' 
Eriksen et al.

Based on: 'The environmental footprint of the Dutch healthcare sector: beyond environmental impact'
Steenmeijer MA, Rodrigues JFD, Zijp MC, Waaijers-van der Loop SL
The Lancet Planetary Health

Tasks main.py:
    
    1. Prepare paths
    2. Load data from background EE-IOA objects and Statistics NL / Or with input from another country
    3. Prepare labels and classifications
    4. Perform EE-IOA calculation
    5. Adding direct impacts and other healthcare specific impacts
    6. Compile final results
    7. Process results for output files
    8. Diagnostics

@authors: Michelle A. Steenmeijer & Joao F. D. Rodrigues
@Editor: Ofir Eriksen

"""
import pandas as pd
import numpy as np
import numpy.matlib
import os
import sys
import matplotlib.pyplot as plt
from .functions_2025 import *
from analysis.constants import AR6_GWP100, eriksen_folder
from paths import (
    BRONZE_DIR,
    BACKGROUND_DIR,
    MRIO_DIR,
    OUTPUT_DIR,
    EXIOBASE_DIR,
    SILVER_INPUT_DIR,
    ensure_runtime_directories,
)
from matplotlib.backends.backend_pdf import PdfPages # Added this to save multiple plots in one pdf
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# This option determines the way floating point numbers, arrays and other NumPy objects are displayed.
np.set_printoptions(precision=2) 

##############################################
# 1) Prepare paths
##############################################

# Resolve paths from this file, not from the caller's current directory.
ensure_runtime_directories()
mainpath = str(BRONZE_DIR.parent.parent)
data_dir = str(BRONZE_DIR) + os.sep
bg_dir = str(BACKGROUND_DIR) + os.sep
mrio_dir = str(MRIO_DIR) + os.sep
# Output routing. The default boundary writes the headline replication folder;
# any OTHER scope writes to its own scenario folder instead.
#
# Without this, a scenario run silently overwrote the headline results - running
# HC_SCOPE=zorg_en_welzijn replaced the 4,713 kt default with the 5,282 kt
# childcare-inclusive figure in 01_eriksen_replication, with nothing in the
# output to say which boundary the numbers belonged to. The scope is also
# recorded in the folder so a stale scenario cannot be mistaken for a current
# one.
_SCOPE = os.environ.get("HC_SCOPE", "health_eldercare")
if _SCOPE == "health_eldercare":
    output_dir = os.path.join(str(OUTPUT_DIR), *eriksen_folder().split("/"))
else:
    output_dir = os.path.join(str(OUTPUT_DIR), "scenarios", _SCOPE)
os.makedirs(output_dir, exist_ok=True)
print(f"scope boundary '{_SCOPE}' -> {output_dir}")
os.makedirs(output_dir, exist_ok=True)

# Intermediate workbooks that only eriksen_tables.py reads back. They are a
# handoff between two scripts, not a deliverable, so by the medallion
# contract they belong in silver rather than in gold's output_dir above.
if _SCOPE == "health_eldercare":
    interim_dir = os.path.join(str(SILVER_INPUT_DIR), "eriksen_interim",
                               *eriksen_folder().split("/"))
else:
    interim_dir = os.path.join(str(SILVER_INPUT_DIR), "eriksen_interim",
                               "scenarios", _SCOPE)
os.makedirs(interim_dir, exist_ok=True)

# 2C) Find and import background.py
# if not found, add to the code before importing: 
#code_dir = mainpath + '\\scripts\\'
#os.chdir(code_dir)
## back to main file 
#os.chdir(mainpath)


##############################################
# 2) Retrieve data
##############################################

## This section has been changed radically. Old code can still be found further down
## The code adds a switch to change between country specific data (DK / NL)
 
# Choose mode
mode = "Danish"  # or "Dutch"

# ---------------------------------------------------------------------------
# Analysis-year configuration. 2022 is the primary year (Danish 2022
# expenditure on the EXIOBASE v3.8.2 IOT_2022_ixi background built by
# pipelines.prep_background_2022); 2019 is the pre-COVID validation baseline
# (Danish 2019 detailed-SUT expenditure on EXIOBASE 3.8.2's 2016 table).
# Select with HC_ANALYSIS_YEAR=2019|2022 (default 2022).
ANALYSIS_YEAR = os.environ.get("HC_ANALYSIS_YEAR", "2022")
# Scope-boundary scenario. "health_eldercare" (default) = SHA health + residential
# eldercare, the manuscript boundary. "health_only" drops eldercare (12401/13302);
# "zorg_en_welzijn" adds childcare (12402/13301), matching the expansive Dutch
# "health and welfare" boundary of Steenmeijer et al. 2022.
SCOPE_SCENARIO = os.environ.get("HC_SCOPE", "health_eldercare")
INCLUDE_CHILDCARE = SCOPE_SCENARIO == "zorg_en_welzijn"
INCLUDE_ELDERCARE = SCOPE_SCENARIO != "health_only"
BACKGROUND_YEAR = "2022" if ANALYSIS_YEAR == "2022" else "2016"
# Optional model variant, e.g. HC_BACKGROUND_TAG=_snacship selects the
# background with the Danish shipping reallocation applied. Empty = as published.
BACKGROUND_YEAR = BACKGROUND_YEAR + os.environ.get("HC_BACKGROUND_TAG", "")
# Danmarks Nationalbank annual average DKK/EUR
DKK_PER_EUR_BY_YEAR = {"2019": 7.4661, "2022": 7.4396}
# Direct healthcare waste components from Statistics Denmark AFFALD01 (total
# waste excl. soil, tonnes): QA human health, 870000 residential care, 880000
# social work. Combined below with the SAME year-specific eldercare share that
# DRIVHUS uses, so the two direct accounts stay consistent.
_AFFALD_T = {"2019": dict(qa=28763, res=7460, soc=13214),
             "2022": dict(qa=30289, res=8422, soc=13084)}[ANALYSIS_YEAR]
year = BACKGROUND_YEAR  # background pickle year (also used by the Dutch mode)

## Adding extra_functions.py to calculate 3 new expenditure vectors
## This is where another country can be added, if the data is available in a similar format as the Danish data

from .extra_functions import (
    calculate_healthcare_totals,
    calculate_healthcare_totals_2022,
    eldercare_share_of_social_work,
    eldercare_share_of_social_work_io,
)
if ANALYSIS_YEAR == "2022":
    hc51, hc52, healthcare_services, expenditure_breakdown = calculate_healthcare_totals_2022(
        BRONZE_DIR / "input_output" / "2016_2022" / "input_output_en_2022.xlsx",
        include_childcare=INCLUDE_CHILDCARE, include_eldercare=INCLUDE_ELDERCARE,
    )
else:
    hc51, hc52, healthcare_services, expenditure_breakdown = calculate_healthcare_totals(
        BRONZE_DIR / "dk_umat_2019.xlsx",
        include_childcare=INCLUDE_CHILDCARE, include_eldercare=INCLUDE_ELDERCARE,
    )
# Provenance record: every (purpose x transaction) column that entered the totals.
expenditure_breakdown.to_csv(
    SILVER_INPUT_DIR / f"dk_expenditure_breakdown_{ANALYSIS_YEAR}.csv", index=False
)

print("HC.51:", hc51)
print("HC.52:", hc52)
print("Healthcare Services (incl. full eldercare, all individual-consumption transactions):", healthcare_services)

# Load CBS data depending on mode
if mode == "Dutch":
    cbs_data = pd.read_csv(os.path.join(data_dir, 'nl_cbs_data_2016.csv'), index_col=['Index', 'Unit'])
    if 'ISO2' not in cbs_data.columns or set(cbs_data['ISO2']) != {'NL'}:
        raise ValueError("Expected Netherlands data with ISO2=NL")
else:
        
      
# === Source values (kDKK) → MEUR and overwrite Silver DK input; set Conversion=1.0 ===
    # Conversion=1.0 because both expenditure sources are at BASIC prices, matching
    # EXIOBASE's valuation: the 2019 route reads sheet 'Ubas' of the detailed use
    # table; the 2022 route sums only the industry-coded (basic-price) rows of the
    # public IO workbook, excluding its separate product-tax/VAT rows.
    # Currency: Danmarks Nationalbank annual average DKK/EUR for the analysis year;
    # source values are in 1000 DKK (kDKK), so MEUR = kDKK / (rate * 1000).

    DKK_PER_EUR = DKK_PER_EUR_BY_YEAR[ANALYSIS_YEAR]
    KDKK_TO_MEUR = 1.0 / (DKK_PER_EUR * 1000.0)
    hc51_meur = float(hc51) * KDKK_TO_MEUR            # Pharm (HC.51)
    hc52_meur = float(hc52) * KDKK_TO_MEUR            # MedAppl (HC.52)
    healthcare_services_meur = float(healthcare_services) * KDKK_TO_MEUR  # HC services

    # Overwrite the derived Silver input with these MEUR values and Conversion=1.0.
    dk_csv_path = str(SILVER_INPUT_DIR / 'dk_data_2025.csv')
    df = pd.read_csv(dk_csv_path)

    # Ensure required columns exist
    if 'Index' not in df.columns:
        raise KeyError("Expected column 'Index' in dk_data_2025.csv")
    if 'Unit' not in df.columns:
        # Insert Unit as 2nd column if missing
        df.insert(1, 'Unit', '')
    if 'ISO2' not in df.columns:
        raise KeyError("Expected ISO2 country column in dk_data_2025.csv")
    if not (df['ISO2'] == 'DK').all():
        raise ValueError("Expected Denmark (ISO2=DK) data in dk_data_2025.csv")

    # Ensure required rows exist; create if absent
    required_rows = ['Expenditure', 'Conversion', 'DirectEm']
    for r in required_rows:
        if r not in df['Index'].values:
            new_row = {'Index': r, 'Unit': 'na', 'ISO2': 'DK'}
            for col in ['HC service', 'Pharm', 'MedAppl']:
                if col not in df.columns:
                    raise KeyError(f"Missing expected column '{col}' in dk_data_2025.csv")
                new_row[col] = 0.0
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Update Expenditure row (MEUR)
    df.loc[df['Index'] == 'Expenditure', 'Unit'] = 'MEUR'
    df.loc[df['Index'] == 'Expenditure', 'HC service'] = healthcare_services_meur
    df.loc[df['Index'] == 'Expenditure', 'Pharm']      = hc51_meur
    df.loc[df['Index'] == 'Expenditure', 'MedAppl']    = hc52_meur

    # Set Conversion row to 1.0 for all used columns
    df.loc[df['Index'] == 'Conversion', 'Unit'] = 'na'
    for col in ['HC service', 'Pharm', 'MedAppl']:
        df.loc[df['Index'] == 'Conversion', col] = 1.0

    # === Direct (operational, Scope 1) emissions of the Danish healthcare scope ===
    # Statistics Denmark DRIVHUS greenhouse-gas accounts by industry (kt CO2e, excl. CO2
    # from biomass; see data/bronze/dk_direct_emissions_drivhus.csv for provenance).
    # Scope construction mirrors the expenditure boundary (health + eldercare):
    #   QA Human health (86) + Residential care (870000)
    #   + eldercare share of Social work without accommodation (880000), where the share
    #     is derived from the use/supply tables (split of 880000 products between
    #     purposes 12401 eldercare and 12402 childcare),
    #   - hospital N2O (medical/anaesthetic N2O sits inside the accounts; it is removed
    #     here because anaesthetic gases enter separately as bottom-up item B_ANAE -
    #     the same medical-gas exclusion Steenmeijer et al. apply to the CBS figure).
    DRIVHUS_YEAR = int(ANALYSIS_YEAR)  # matches the expenditure year
    _drivhus = pd.read_csv(BRONZE_DIR / "dk_direct_emissions_drivhus.csv", comment="#")
    _dh = _drivhus[_drivhus["year"] == DRIVHUS_YEAR].set_index(["industry_code", "emtype"])[
        "value_kt_co2e"
    ]
    if ANALYSIS_YEAR == "2022":
        # read the share from the analysis year's own IO table (industry 880000's
        # deliveries to eldercare vs childcare) rather than carrying the 2019
        # SUT-derived value forward
        alpha_eldercare = eldercare_share_of_social_work_io(
            BRONZE_DIR / "input_output" / "2016_2022" / "input_output_en_2022.xlsx")
    else:
        alpha_eldercare = eldercare_share_of_social_work(BRONZE_DIR / "dk_umat_2019.xlsx")
    direct_em_kt = (
        _dh[("VQA", "GHGEXBIO")]
        + _dh[("V870000", "GHGEXBIO")]
        + alpha_eldercare * _dh[("V880000", "GHGEXBIO")]
        - _dh[("V860010", "N2O")]
    )
    print(
        f"Direct operational emissions (DRIVHUS {DRIVHUS_YEAR}): "
        f"QA {_dh[('VQA','GHGEXBIO')]} + 87 {_dh[('V870000','GHGEXBIO')]} "
        f"+ {alpha_eldercare:.4f}*88 {_dh[('V880000','GHGEXBIO')]} - hosp N2O {_dh[('V860010','N2O')]} "
        f"= {direct_em_kt:.1f} kt CO2e"
    )
    df.loc[df['Index'] == 'DirectEm', 'Unit'] = 'kt CO2e'
    for col in ['HC service', 'Pharm', 'MedAppl']:
        df.loc[df['Index'] == 'DirectEm', col] = 0.0
    df.loc[df['Index'] == 'DirectEm', 'HC service'] = float(direct_em_kt)
    DK_DIRECT_WASTE_KT = (_AFFALD_T["qa"] + _AFFALD_T["res"]
                          + alpha_eldercare * _AFFALD_T["soc"]) / 1e3
    print(f"Direct healthcare waste (AFFALD01 {DRIVHUS_YEAR}, alpha={alpha_eldercare:.4f}): "
          f"{DK_DIRECT_WASTE_KT:.1f} kt")

    df.to_csv(dk_csv_path, index=False)
    print(f"DK SUT overwrite: MEUR totals written, Conversion=1.0, DirectEm={float(direct_em_kt):.1f} kt → {dk_csv_path}")



# The following 3 lines of code were commented out, firstly because it stopped working (maybe CBS changed something in their APIs),
# secondly because it was not needed anymore, since the data is now retrieved from the UMAT file
# 2A) Retrieve CBS data for 2016. If not needed to update, uncomment and only run next line
#cbs_data = get_cbsdata(data_dir)  # Retrieve most up to date CBS data, can comment out after the first time
#cbs_data = pd.read_csv('cbs_data_2016.tsv', sep = '\t', index_col = [0, 1])  # Retrieve earlier compiled CBS data


#The following code is added instead of "get_cbsdata". This code retrieves and saves data into "Dk_data_2025"

cbs_data = pd.read_csv(str(SILVER_INPUT_DIR / 'dk_data_2025.csv'), index_col=['Index', 'Unit'])
print("Expenditure data loaded from DK SUT CSV (MEUR).")

# Assert Conversion row exists and equals 1.0 for used columns
if ('Conversion', 'na') not in cbs_data.index:
    raise KeyError("Expected ('Conversion','na') row not found in dk_data_2025.csv")
conv_row = cbs_data.loc[('Conversion', 'na')]
for col in ['HC service', 'Pharm', 'MedAppl']:
    if col in conv_row.index:
        assert float(conv_row[col]) == 1.0, f"Conversion factor for '{col}' must be 1.0"


bp_HCserv = cbs_data.iloc[0, 0].item()
bp_phar   = cbs_data.iloc[0, 1].item() * cbs_data.iloc[1, 1].item()  # == ×1.0
bp_appl   = cbs_data.iloc[0, 2].item() * cbs_data.iloc[1, 2].item()  # == ×1.0
print("Using SUT MEUR (Conversion=1.0):",
      "HC services =", bp_HCserv,
      "Pharm =", bp_phar,
      "MedAppl =", bp_appl)


# 2B) Create background object
# That is, containing exiobase and stimulus
year = BACKGROUND_YEAR
#To rerun a second time faster comment the next
#line and uncomment the follow-up ones
bg = createBackground(mrio_dir, cbs_data, bg_dir, year)  

# ---------------------------------------------------------------------------
# Direct waste: overwrite the background's own value with the Danish account.
#
# createBackground derives the health sector's direct waste from the 2011
# hybrid extension. This study replaces it with Statistics Denmark's AFFALD01
# (see DK_DIRECT_WASTE_KT above), exactly as DRIVHUS replaces the direct
# greenhouse-gas figure.
#
# The replacement used to be applied only where the results were tabulated, so
# Hstim itself still carried the hybrid value and any module reading the
# background directly - the capital sensitivity did - got a direct waste of
# 160.0 kt instead of the Danish 42.8 kt. Correcting it here makes the
# background the single source of truth for every consumer, and the corrected
# object is persisted so downstream modules load the same numbers.
# ---------------------------------------------------------------------------
_ROW_WASTE = 6
_hybrid_direct_waste = float(bg["Hstim"][_ROW_WASTE, 0])
bg["Hstim"][_ROW_WASTE, :] = 0.0
bg["Hstim"][_ROW_WASTE, 0] = DK_DIRECT_WASTE_KT
print(f"Direct waste replaced in background: hybrid {_hybrid_direct_waste:.1f} kt "
      f"-> AFFALD01 {DK_DIRECT_WASTE_KT:.1f} kt")
# Persist ONLY for the default boundary. The background is shared by every
# downstream module, so writing it from a scenario run would silently give them
# that scenario's numbers: a zorg_en_welzijn run put the childcare-inclusive
# total into the scope partition, which the consistency audit caught.
# The write is also made idempotent. Every downstream freshness check compares
# a gold file's mtime with this file's, so re-running the pipeline to rebuild
# one table used to mark all the others stale even though the background had
# not changed by a single byte. Only write when the content actually differs.
if _SCOPE == "health_eldercare":
    _bg_path = os.path.join(bg_dir, f"gddz_background_information_{year}.pkl")
    _payload = pkl.dumps(bg)
    _same = False
    if os.path.exists(_bg_path):
        with open(_bg_path, "rb") as _fh:
            _same = _fh.read() == _payload
    if _same:
        print(f"background unchanged, keeping {os.path.basename(_bg_path)} "
              f"and its timestamp")
    else:
        with open(_bg_path, "wb") as _fh:
            _fh.write(_payload)
else:
    print(f"scenario boundary '{_SCOPE}': background NOT persisted, so "
          f"downstream modules keep the default boundary")
#bg_tmp = open(excel_dir + 'gddz_background_information.pkl',"rb")
#bg = pkl.load(bg_tmp)
#bg_tmp.close()



##############################################
#3)  Create labels, classification (incl for aggregation)
##############################################


# 3A) Labels name countries/regions
reg_labels = bg['label']['region'][['ISO3', 'Name', 'DESIRE region name']]
reg_labels.columns = ['ISO3','RegName', 'Region']

df_labels = {'sectxtcode' : list(bg['label']['industry'].reset_index()['CodeTxt']) * 49,
             'secname':list(bg['label']['industry']['Name']) * 49,
             'regiso3': np.repeat(list(bg['label']['region']["ISO3"]), 163),
             'regname':np.repeat(list(bg['label']['region']["Name"]), 163),
             'regregioncode': np.repeat(list(bg['label']['region']["DESIRE region"]), 163),
             'regregionname':np.repeat(list(bg['label']['region']["DESIRE region name"]), 163),
             }


# 3B) Labels impact categories > selection can be changed in background file
char_labels = []
for k in range(len(bg['label']['characterization'])):
    chts = str(bg['label']['characterization']['Name'][k]) + ' (' + str(bg['label']['characterization']['Unit'][k]) + ')'
    char_labels.append(chts)
cols_impcat = [x for x in char_labels if x not in ['Value added (M.EUR)', 'Employment (1000 p.)']]


# 3C) Labels industry aggregation
excel_str = 'classifications.xlsx'
sheet_str = 'disagg_ind'  
sec_labels = pd.read_excel(EXIOBASE_DIR / excel_str, sheet_name = sheet_str, skiprows = 5)
sec_labels = sec_labels[['Code', 'Description', 'AggPos', 'AggDescription', 'AggCode', 'Scope', 'Scope_hotspot']]
sec_labels.rename(columns={'Code':'SecTxtCode', 'Description':'SecName', 'AggPos':'SAggPos', 'AggDescription':'SAggDescription', 'AggCode':'SAggCode'}, inplace = True)
fig_labels = pd.read_excel(EXIOBASE_DIR / excel_str, sheet_name = 'agg_ind_fig', skiprows = 5)


# 3D) Create multi-index for 163 sectors and 49 regions
multiindex = pd.MultiIndex.from_tuples(list(zip(list(df_labels['regiso3']), list(df_labels['sectxtcode']))))



##############################################
# 4)  EE-IOA footprint calculation
##############################################

# Arrays results
array_contrib = calc_contrib(bg['B'], bg['L'], bg['Ystim'])
array_hotspot = calc_hotspot(bg['B'], bg['L'], bg['Ystim'])

# Turn arrays to dataframes
df_contrib = df_fromarray(array_contrib, char_labels, multiindex, cols_impcat)
df_hotspot = df_fromarray(array_hotspot, char_labels, multiindex, cols_impcat)

#Definition of the 4 dataframes
# df_contrib and df_hotspot are lists of 4 dataframes:
# df_contrib[0]/df_hotspot[0] = result for the total expenditure vector (Healthcare Services + Pharmaceuticals and consumables + Medical durables goods)
# df_contrib[1]/df_hotspot[1] = result for the expenditure vector for Healthcare Services
# df_contrib[0]/df_hotspot[0] = result for the expenditure vector for Pharmaceuticals and consumables
# df_contrib[0]/df_hotspot[0] = result for the expenditure vector for Medical durables goods


##############################################
# 5) Adding direct impacts and other healthcare specific impacts
##############################################


# ===================== DK scaling of direct bottom-up emissions =====================
# This step reads the NL base bottom-up file, scales *direct* emissions to DK,
# recomputes totals, and writes dk_bottomup_data_2025.txt for the rest of the pipeline.



import re
import tempfile

def _safe_atomic_write(target_path: str, content: str) -> None:
    """Atomically replace a text file without leaving backup artifacts."""
    d = os.path.dirname(target_path) or "."
    os.makedirs(d, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=d,
            prefix=".pipeline_", suffix=".tmp", delete=False
        ) as handle:
            handle.write(content)
            tmp = handle.name
        os.replace(tmp, target_path)
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)

def scale_bottomup_all_to_dk(
    base_path: str,
    target_path: str,
    factors: dict,
    round_digits: int = None
) -> None:
    """
    Scale ALL impact columns for the four bottom-up sources using multiplicative factors (NL → DK):
      - Anaesthetic → factors["Anaesthetic"]
      - pMDI → factors["pMDI"]
      - Commute (direct+indirect) → factors["Commute"]
      - Visitor travel (direct+indirect) → factors["Visitor travel"]
    Then recompute '(total)' rows as (direct + indirect) across ALL columns and write TSV.
    """
    # Load base (NL) bottom-up data
    df = pd.read_csv(base_path, sep="\t").set_index("Source")

    if "ISO2" not in df.columns:
        raise KeyError(f"Missing ISO2 country column in {base_path}")
    if not (df["ISO2"] == "NL").all():
        raise ValueError(f"Expected NL bottom-up source data in {base_path}")

    # Validate presence of rows and factor keys
    required_rows = [
        "Anaesthetic", "pMDI",
        "Commute (direct)", "Commute (indirect)", "Commute (total)",
        "Visitor travel (direct)", "Visitor travel (indirect)", "Visitor travel (total)",
    ]
    missing_rows = [r for r in required_rows if r not in df.index]
    if missing_rows:
        raise KeyError(f"Missing expected rows in {base_path}: {missing_rows}")

    required_factors = ["Anaesthetic", "pMDI", "Commute", "Visitor travel"]
    missing_f = [k for k in required_factors if k not in factors]
    if missing_f:
        raise KeyError(f"Missing required scaling factors: {missing_f}")

    # Identify numeric columns (all except the index)
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    # 1) Scale standalone rows (Anaesthetic, pMDI) across ALL columns
    df.loc["Anaesthetic", num_cols] *= float(factors["Anaesthetic"])
    df.loc["pMDI",       num_cols] *= float(factors["pMDI"])

    # 2) Scale Commute (both direct and indirect)
    df.loc["Commute (direct)",  num_cols] *= float(factors["Commute"])
    df.loc["Commute (indirect)",num_cols] *= float(factors["Commute"])

    # 3) Scale Visitor travel (both direct and indirect)
    df.loc["Visitor travel (direct)",  num_cols] *= float(factors["Visitor travel"])
    df.loc["Visitor travel (indirect)",num_cols] *= float(factors["Visitor travel"])

    # 4) Recompute totals = direct + indirect (for ALL impact columns)
    for group in ["Commute", "Visitor travel"]:
        df.loc[f"{group} (total)", num_cols] = (
            df.loc[f"{group} (direct)",  num_cols]
            + df.loc[f"{group} (indirect)",num_cols]
        )

    # Optional rounding for readability
    if round_digits is not None:
        df[num_cols] = df[num_cols].round(round_digits)

    # The scaled output is Denmark-specific, even though it retains the NL
    # source rows and categories used as its scaling baseline.
    df["ISO2"] = "DK"

    # Write atomically to target_path
    content = df.reset_index().to_csv(sep="\t", index=False)
    _safe_atomic_write(target_path, content)
    print(f"DK scaling (ALL columns) applied; wrote: {target_path}")

# ---- DK scaling constants and paths (These should be defined BEFORE calling the function) ----
# Commute and visitor factors re-derived from official sources (2026-09 revision):
#   employment ratio = 518,889 / 1,220,750 = 0.42506
#     (DK: DST NABB69 national-accounts employment 2019, industries 86000 + 87880;
#      NL: CBS 2016 health-and-welfare employment used by Steenmeijer et al.)
#   weekly-hours ratio = 34.4 / 29.2 = 1.17808 (as in the original workbook)
#   commuting-distance ratio = 9.0 / 7.88 = 1.14213 km/person/day
#     (DK: TU aarsrapport Danmark 2019, DTU, Table 20; NL: CBS as in workbook)
#   -> Commute = 0.42506 * 1.17808 * 1.14213 = 0.5719
#   Visitor travel = 0.42506 * 1.258097 = 0.5348
#
#   The weekly-hours ratio applies to COMMUTING ONLY. Hours worked scale how
#   often staff travel to work; they do not scale how far patients and visitors
#   travel, which is driven by system size and travel behaviour. The appendix is
#   explicit on this: eq. A10 (commuting) carries the hours term, eqs. A12-A15
#   (patient and visitor) do not. Until 2026-09 this module applied the hours
#   ratio to visitor travel as well, overstating it by 17.8 %.
#   (distance uplift as documented in
#   data/bronze/commuting_private_travel_calculations_2026.xlsx)
# Anaesthetic and pMDI factors are retained only for the (all-zero) non-GWP columns;
# their GWP values are replaced below with Danish primary data.
SCALING_DK_OVER_NL_BY_YEAR = {
    # 2019: employment 518,889 (NABB69, 86000+87880) / 1,220,750; hours 34.4/29.2;
    #       TU 2019 distance 9.0/7.88 km/person/day
    "2019": {"Anaesthetic": 0.67, "pMDI": 0.45, "Commute": 0.5719, "Visitor travel": 0.5348},
    # 2022: employment 556,999 (NABB69 2022: 244,852 + 312,147) / 1,220,750 = 0.45624;
    #       hours 34.4/29.2 = 1.17808; TU aarsrapport 2022 Table 20 distance
    #       9.3/7.88 = 1.18020 -> Commute 0.6343; Visitor 0.45624*1.258097 = 0.5740
    "2022": {"Anaesthetic": 0.67, "pMDI": 0.45, "Commute": 0.6343, "Visitor travel": 0.5740},
}
SCALING_DK_OVER_NL = SCALING_DK_OVER_NL_BY_YEAR[ANALYSIS_YEAR]

BOTTOMUP_BASE = os.path.join(data_dir, "nl_bottomup_data.txt")
BOTTOMUP_2025 = str(SILVER_INPUT_DIR / "dk_bottomup_data_2025.txt")
# ---------------------------------------------------------------------------

# Apply DK scaling and write dk_bottomup_data_2025.txt
scale_bottomup_all_to_dk(
    base_path=BOTTOMUP_BASE,
    target_path=BOTTOMUP_2025,
    factors=SCALING_DK_OVER_NL,
    round_digits=4
)

# ---- Danish primary values for the medical-gas items (replace NL-scaled GWP) ----
# Anaesthetic gases: Denmark's National Inventory Document 2024 (DCE report 622),
#   category 2.G.3.a: 38 t N2O/yr (constant 2013-2022) x 273 kg CO2e/kg N2O
#   (IPCC AR6, the same factor the MRIO climate row uses) = 10.4 kt CO2e.
#   The volatile agents are no longer a population-scaled Dutch proxy: they come
#   from the Danish Medicines Agency register, in the DK_ANAESTHETIC_LITRES
#   block below, which supersedes the 1.4 kt proxy this line used to quote.
#   The two together are the 11.572 kt reported as scope1_anaesthetic. The
#   hospital N2O contained in the DRIVHUS direct-emissions figure was subtracted
#   there, so no double counting.
# pMDI propellants: 7.2 t HFC dispensed in Denmark 2019 (Vestbo & Press-
#   Kristensen 2023, Eur Respir J 62:2300856; ~90% HFC-134a, 10% HFC-227ea),
#   characterised with the ReCiPe 2016 (H) factors used by Steenmeijer et al.
#   (1,549 / 3,860 kg CO2e/kg) = 12.8 kt CO2e. (The widely quoted 31 kt is a
#   GWP20 figure; the Danish EPA F-gas inventory reports 11.6 kt GWP100 for 2022.)
# pMDI by year: 2019 = 7.2 t HFC dispensed (Vestbo & Press-Kristensen 2023) x
# ReCiPe 2016 GWP100 -> 12.8 kt; 2022 = Danish EPA F-gas inventory actual MDI
# emission, 11.6 kt CO2e (Miljoestyrelsen F-gas report, Table 15).
# VOLATILE ANAESTHETICS - Danish primary data replaces the population-scaled
# Dutch proxy (2026-09 revision). Sales of ATC N01AB, entire country, all
# sectors, from the Danish Medicines Agency's medstat.dk register, which is a
# mandatory-reporting register covering all sales in Denmark. Field 11 of
# <year>_atc_code_data.txt is "volume in 1.000 units"; for N01AB the unit is
# millilitres of liquid agent (every marketed product is an inhalation liquid),
# so the field is litres. Cached under data/bronze/medstat/.
#
# Litres of liquid agent sold (verified against the register):
#   2022  sevoflurane 2,400  desflurane 181  isoflurane 15
#   2019  sevoflurane 2,714  desflurane 400  isoflurane 17
#
# Converted with densities at 20 C from Laster, Fang & Eger (1994, Anesth Analg
# 78:1152) and the GWP100 values recommended by Sulbaek Andersen, Nielsen &
# Sherman (2023, Lancet Planet Health 7:e622) - the same set used by Talbot et
# al. (2025) and by Caviglia et al. (2025), whose study covers Denmark from this
# same register. A 5% downward correction is applied to sevoflurane for the
# fraction metabolised rather than exhaled (MacNeill et al. 2017; Schuster 2020).
#
# The N2O term: Denmark's National Inventory Document 2024 (DCE report 622)
# category 2.G.3.a, a constant 38 t N2O/yr for 2013-2022, characterised on the
# same AR6 factor the MRIO climate row uses.
#
# It used to carry AR4's 298, chosen when the MRIO row still ran on EXIOBASE's
# own DESIRE factors, which are AR4. The MRIO row moved to AR6 and this term did
# not, which left the study mixing two vintages in one total: 38 t x (298 - 273)
# = 0.95 kt CO2e. Reading the factor from AR6_GWP100 rather than restating it
# means the two cannot drift apart again.
#
# Hospital N2O was subtracted from the DRIVHUS direct figure, so there is no
# double counting.
DK_ANAESTHETIC_LITRES = {
    "2019": {"sevoflurane": 2714.0, "desflurane": 400.0, "isoflurane": 17.0},
    "2022": {"sevoflurane": 2400.0, "desflurane": 181.0, "isoflurane": 15.0},
}[ANALYSIS_YEAR]
DK_ANAESTHETIC_DENSITY_KG_PER_L = {"sevoflurane": 1.5203, "desflurane": 1.4651,
                                   "isoflurane": 1.5019}
DK_ANAESTHETIC_GWP100 = {"sevoflurane": 144.0, "desflurane": 2590.0,
                         "isoflurane": 539.0}
DK_ANAESTHETIC_EXHALED = {"sevoflurane": 0.95, "desflurane": 1.0,
                          "isoflurane": 1.0}
DK_VOLATILE_KT_CO2E = sum(
    DK_ANAESTHETIC_LITRES[a] * DK_ANAESTHETIC_DENSITY_KG_PER_L[a]
    * DK_ANAESTHETIC_EXHALED[a] * DK_ANAESTHETIC_GWP100[a]
    for a in DK_ANAESTHETIC_LITRES) / 1e6           # kg -> kt
DK_N2O_KT_CO2E = 38.0 * AR6_GWP100["N2O"] / 1e3
DK_ANAESTHETIC_KT_CO2E = DK_N2O_KT_CO2E + DK_VOLATILE_KT_CO2E
DK_PMDI_KT_CO2E = {"2019": 12.8, "2022": 11.6}[ANALYSIS_YEAR]
# Direct healthcare waste (Statistics Denmark AFFALD01, total waste excl. soil,
# QA + 870000 + alpha x 880000 with the 2019-derived eldercare share 0.4914):
# 2019: 28,763 + 7,460 + 0.4914*13,214 = 42.7 kt; 2022: 30,289 + 8,422 +
# 0.4914*13,084 = 45.1 kt. Replaces the hybrid-2011-derived direct waste entry
# of the B_HEAL row, mirroring the DRIVHUS replacement for GWP.
_bu = pd.read_csv(BOTTOMUP_2025, sep="\t").set_index("Source")
# PATIENT AND VISITOR TRAVEL - Danish primary data replaces the England->NL->DK
# double transplant (2026-09 revision). The Dutch item is a whole-POPULATION
# quantity (159 km/resident/year from the English National Travel Survey, applied
# to 16.98 M residents), so scaling it by an employment ratio and by average
# weekly working hours - as the previous factor did - was a unit error: those
# belong to commuting only.
#
# Denmark has its own measurement. Transportvaneundersoegelsen (TU), DTU Center
# for Transport Analytics, Tabel 15 "Antal ture, afstand og tid fordelt paa
# turformaal", purpose code 33 "Social/sundhed" (visits to doctor, hospital,
# jobcentre): 0.9 km/person/day in 2019 and 0.8 in 2022, against all-purpose
# totals of 40.4 and 37.5 km/person/day. Read from the published reports cached
# under data/bronze/tu_travel/. The TU universe is residents aged 6 and over.
#
# Visitor travel has no Danish source - TU folds hospital visits into
# "Besoege familie/venner" - so it is carried as one clearly labelled imported
# parameter: the NHS England ratio of visitor to patient travel, 0.29/1.23 =
# 0.236 (Tennison et al. 2021, appendix 1 table S12).
#
# The emission intensity is the Dutch composite implied by Steenmeijer et al.
# (358.6386 kt over 2.7 bn person-km = 0.1328 kg CO2e/person-km), retained so
# the item stays methodologically comparable with the template.
DK_TRAVEL_KM_PER_PERSON_DAY = {"2019": 0.9, "2022": 0.8}[ANALYSIS_YEAR]
DK_POPULATION_6PLUS = {"2019": 5_442_766, "2022": 5_499_115}[ANALYSIS_YEAR]
DK_TRAVEL_INTENSITY_KG_PER_PKM = 0.1328
DK_VISITOR_TO_PATIENT_RATIO = 0.236
_pkm = DK_TRAVEL_KM_PER_PERSON_DAY * 365.0 * DK_POPULATION_6PLUS
DK_PATIENT_TRAVEL_KT_CO2E = _pkm * DK_TRAVEL_INTENSITY_KG_PER_PKM / 1e6
DK_VISITOR_TRAVEL_KT_CO2E = DK_PATIENT_TRAVEL_KT_CO2E * DK_VISITOR_TO_PATIENT_RATIO
DK_PATIENT_VISITOR_TRAVEL_KT_CO2E = (DK_PATIENT_TRAVEL_KT_CO2E
                                     + DK_VISITOR_TRAVEL_KT_CO2E)

_bu.loc["Anaesthetic", "Global warming (ktCO2eq)"] = DK_ANAESTHETIC_KT_CO2E
_bu.loc["pMDI", "Global warming (ktCO2eq)"] = DK_PMDI_KT_CO2E
# Rewrite the patient/visitor travel rows to the Danish primary total, keeping
# the direct/indirect split of the Dutch source so the transport-mode structure
# is preserved.
_vt_rows = ["Visitor travel (direct)", "Visitor travel (indirect)"]
_vt_old = _bu.loc[_vt_rows, "Global warming (ktCO2eq)"].astype(float)
if _vt_old.sum() > 0:
    _bu.loc[_vt_rows, "Global warming (ktCO2eq)"] = (
        DK_PATIENT_VISITOR_TRAVEL_KT_CO2E * _vt_old / _vt_old.sum()).values
if "Visitor travel (total)" in _bu.index:
    _bu.loc["Visitor travel (total)", "Global warming (ktCO2eq)"] = \
        DK_PATIENT_VISITOR_TRAVEL_KT_CO2E
_safe_atomic_write(BOTTOMUP_2025, _bu.reset_index().to_csv(sep="\t", index=False))
print(f"Danish primary bottom-up values written:")
print(f"  anaesthetic {DK_ANAESTHETIC_KT_CO2E:.2f} kt CO2e "
      f"(N2O {DK_N2O_KT_CO2E:.2f} + volatiles {DK_VOLATILE_KT_CO2E:.2f}, "
      f"medstat N01AB {ANALYSIS_YEAR})")
print(f"  pMDI {DK_PMDI_KT_CO2E} kt CO2e")
print(f"  patient travel {DK_PATIENT_TRAVEL_KT_CO2E:.1f} + visitor "
      f"{DK_VISITOR_TRAVEL_KT_CO2E:.1f} = "
      f"{DK_PATIENT_VISITOR_TRAVEL_KT_CO2E:.1f} kt CO2e "
      f"(TU {DK_TRAVEL_KM_PER_PERSON_DAY} km/person/day)")
# ===================== End of DK scaling of direct bottom-up emissions =====================





# 5B)

cols_df = df_contrib[0].columns  # same for all

# Adding the direct healthcare emissions from bg['Hstim']
# (Steenmeijer design restored: the GWP entry of Hstim is the national-accounts
# direct emission of the sector - here the DRIVHUS-based figure written to
# dk_data_2025.csv above, excluding medical N2O which enters via B_ANAE - while
# the other four impact categories keep the EXIOBASE-based direct estimates.
# The previous revision computed this row as B x (L·Ystim) over the DK health
# rows, i.e. the MRIO-induced intra-health emissions (~1.4 kt CO2e): that value
# is not the sector's direct emissions and is already contained in the MRIO
# contribution totals; see docs/revision/bug_and_method_fixes.md.)
hc_dir_row = pd.Series(['DNK', 'B_HEAL',
                        bg['Hstim'][:, 0][0],   # Global warming (ktCO2eq), DRIVHUS-based
                        bg['Hstim'][:, 0][1],   # Material extraction (kt)
                        bg['Hstim'][:, 0][2],   # Blue water (Mm3)
                        bg['Hstim'][:, 0][3],   # Land use (km2)
                        DK_DIRECT_WASTE_KT],    # Waste (kt), AFFALD01-based (set below)
                       index=cols_df)


# Reading in an additional file filled with data concerning the additional impact sources
BU_data = pd.read_csv(BOTTOMUP_2025, sep ='\t').set_index('Source')
# The ISO2 provenance column was added to the silver file after the original
# runs; drop it so the impact-value rows keep the width the code expects.
BU_data = BU_data.drop(columns=['ISO2'], errors='ignore')

# Adding the direct emissions from anaesthetic gases 
# (Venema et al., 2022)
anae_cc = BU_data.loc['Anaesthetic','Global warming (ktCO2eq)'].item()
anae_row = pd.Series(['DNK','B_ANAE', anae_cc, 0, 0, 0, 0], index = cols_df)

# Adding the direct emissions from pressurised metered dose inhaler 
# (Wichers & Pieters, 2022)
mdi_cc = BU_data.loc['pMDI','Global warming (ktCO2eq)'].item() 
mdi_row = pd.Series(['DNK', 'B_PMDI', mdi_cc, 0, 0 ,0 ,0], index = cols_df) 


# Adding the impact from individual travel
# The following are the final values calculated using ecoinvent (a licenced LCI), 
# based on the calculation described in the appendix. 

# Calculated impact from commuting
# ..for the contribution analysis
commute_c_row = pd.Series(['DNK', 'B_COMM'] +  list(BU_data.loc['Commute (total)']), index = cols_df)
# ..split in direct en indirect impacts for the hotspot analysis
commute_h_dir_row = pd.Series(['DNK', 'B_COMM'] + list(BU_data.loc['Commute (direct)']), index = cols_df)
commute_h_indir_row = pd.Series(['GLO', 'B_REST'] + list(BU_data.loc['Commute (indirect)']), index = cols_df)

# Calculated impact from travel by patients and visitors
visit_c_row = pd.Series(['DNK', 'B_VISI'] + list(BU_data.loc['Visitor travel (total)']), index = cols_df) 
# ..split in direct en indirect impacts for the hotspot analysis
visit_h_dir_row = pd.Series(['DNK', 'B_VISI'] + list(BU_data.loc['Visitor travel (direct)']), index = cols_df) 
visit_h_indir_row = pd.Series(['GLO', 'B_REST'] + list(BU_data.loc['Visitor travel (indirect)']), index = cols_df) 



##############################################
# 6) Compile total results
##############################################

# 6A) Append the additional rows to the input-output results
rows_c = [hc_dir_row, anae_row, mdi_row, commute_c_row, visit_c_row]
add_rows_c = pd.concat(rows_c, axis = 1, ignore_index=True).T

rows_h = [hc_dir_row, anae_row, mdi_row,
          commute_h_dir_row, commute_h_indir_row,
          visit_h_dir_row, visit_h_indir_row]
add_rows_h = pd.concat(rows_h, axis = 1, ignore_index=True).T

# append all additional rows to main dfs
df_contrib[0] = pd.concat([df_contrib[0], add_rows_c], ignore_index = True)
df_contrib[1] = pd.concat([df_contrib[1], add_rows_c], ignore_index = True)

df_hotspot[0] = pd.concat([df_hotspot[0], add_rows_h], ignore_index = True)
df_hotspot[1] = pd.concat([df_hotspot[1], add_rows_h], ignore_index = True)

# 6B)  Add region and sector aggregation & labels
# .. for the contribution analysis
df_c = []
for x in df_contrib:
    x = pd.merge(x, reg_labels, on = 'ISO3', how = 'left' )
    x = pd.merge(x, sec_labels[['SecTxtCode', 'SecName','SAggDescription', 'Scope']], on = 'SecTxtCode', how = 'left' )
    df_c.append(x)

# .. for the hotspot analysis
df_h = []
for x in df_hotspot:
    x = pd.merge(x, reg_labels, on = 'ISO3', how = 'left' )
    x = pd.merge(x, sec_labels[['SecTxtCode', 'SecName', 'SAggDescription', 'Scope_hotspot']], on = 'SecTxtCode', how = 'left' )
    x.rename(columns = {'Scope_hotspot': 'Scope'}, inplace = True)
    df_h.append(x)



##############################################
# 7) Output final results
##############################################
# Please note that this script read the most up-to-date data from Statistics 
# Netherlands (CBS), which can mean that the health care expenditure is 
# different to the results presented in the paper. 
# The conversion from basic price to purchaser price was done using rounded values,
# causing the results from this model to vary slightly (<1%), with insignificant
# implication to the results.

# 7A) Expenditure vector
# column 'Total (MEUR)' is the sum of the expenditure on Healthcare services,
# Pharmaceuticals & consumables and Medical durable goods
cols_Y = ['Total (MEUR)','Healthcare services','Pharmaceuticals and consumables','Medical durables goods']
Y_df = pd.DataFrame(bg['Ystim'], columns = cols_Y, index = multiindex)
Y_df = Y_df.reset_index()
Y_df.columns = ['ISO3', 'SecTxtCode'] + cols_Y
Y_df = pd.merge(Y_df, reg_labels, on = 'ISO3', how = 'left' )
Y_df = pd.merge(Y_df, sec_labels[['SecTxtCode', 'SecName', 'SAggDescription']], on = 'SecTxtCode', how = 'left' )
Y_df = Y_df[['ISO3', 'RegName', 'Region', 'SecTxtCode', 'SecName',
       'SAggDescription'] + cols_Y]

Y_allsec = Y_df.groupby(['SecTxtCode', 'SecName'])[cols_Y].sum()
Y_aggsec_aggreg = Y_df.groupby(['RegName', 'SAggDescription'])[cols_Y].sum()
Y_aggsec = Y_df.groupby(['SAggDescription'])[cols_Y].sum()

# Read expenditure vector to xlsx for several aggregation levels
writer = pd.ExcelWriter(os.path.join(interim_dir, 'expenditure_vector.xlsx'),
                        engine='xlsxwriter')
Y_df.to_excel(writer, sheet_name='full')
Y_allsec.to_excel(writer, sheet_name='allsec')
Y_aggsec_aggreg.to_excel(writer, sheet_name='aggsec_aggreg')
Y_aggsec.to_excel(writer, sheet_name='aggsec')
writer.close()


# 7B) Multipliers / Coefficients / Intensities
# join the impact results with the expenditure vector
mult_all = pd.concat([Y_df.iloc[:,:-3], df_contrib[0].iloc[:163 * 49, 2:]], axis = 1)
mult_all = mult_all[mult_all['Total (MEUR)'] != 0]  # cannot divide by zero
for x in cols_impcat:
    mult_all[x] = mult_all[x].astype('float')

# Aggregate to later get the weighted average per (aggregated) product group
mult_aggsec_aggreg = mult_all.groupby(['RegName', 'SAggDescription'])[['Total (MEUR)', 'Global warming (ktCO2eq)', 'Material extraction (kt)', 'Blue water consumption (Mm3)','Land use (km2)', 'Waste generation (kt)']].sum()
mult_aggsec = mult_all.groupby(['SAggDescription'])[cols_impcat + ['Total (MEUR)']].sum()
mult_allsec = mult_all.groupby(['SecName'])[cols_impcat + ['Total (MEUR)']].sum()

for df in [mult_all, mult_aggsec_aggreg, mult_aggsec, mult_allsec]:
    for x in cols_impcat:
        df[str(x)+'/MEUR'] = df[x] / df['Total (MEUR)']
        del df[x]


# Write coefficients/multipliers/intensities to xlsx for several aggregation levels
writer = pd.ExcelWriter(os.path.join(interim_dir, 'intensities.xlsx'),
                        engine='xlsxwriter')
mult_all.to_excel(writer, sheet_name='full')
mult_allsec.to_excel(writer, sheet_name='allsec')
mult_aggsec_aggreg.to_excel(writer, sheet_name='aggsec_aggreg')
mult_aggsec.to_excel(writer, sheet_name='aggsec')
writer.close()


# 7C) Dataframe for Table 1 
s1 = df_contrib[0].iloc[:,2:].sum()
s2 = df_contrib[1].iloc[:(163 * 49) + 1, 2:].sum()  # total plus direct impacts
s3 = df_contrib[2].iloc[:,2:].sum()
s4 = df_contrib[3].iloc[:,2:].sum()
s_anae = df_contrib[0].iloc[(163 * 49) + 1, -5:]
s_pmdi = df_contrib[0].iloc[(163 * 49) + 2, -5:]
s_travel = df_contrib[0].iloc[(163 * 49) + 3, -5:] + df_contrib[0].iloc[(163 * 49) + 4, -5:]

t1 = pd.concat([s1, s2, s3, s4, s_anae, s_pmdi, s_travel], axis = 1)
t1.columns = ['Total', 'Healthcare services', 'Pharmaceuticals and chemical products',
               'Medical appliances', 'Release of anaesthetic gases', 
               'Release of pMDI propellants', 'Private travel']
t1 = t1.T

bp_HCserv = cbs_data.iloc[0, 0].item()
bp_phar = cbs_data.iloc[0, 1].item() * cbs_data.iloc[1, 1].item()
bp_appl = cbs_data.iloc[0, 2].item() * cbs_data.iloc[1, 2].item()

t1['Expenditure (MEUR)'] = [(bp_HCserv + bp_phar + bp_appl), bp_HCserv, bp_phar, bp_appl, 'NA', 'NA', 'NA']

# Read Table 1 to Excel file
t1.to_excel('table_1.xlsx')


# 7D)  Results Table S5
R_HC = df_contrib[0].iloc[:,2:].sum()  # Healthcare footprint totals

# The following line can be uncommented to find out the region index of a specific country
# print(bg['label']['region'])

# Final consumption footprint
# The line below is where you change from NL to whatever country you want to analyse
# For another country, change also the k_NL variable name and value accordingly
k_DK = 6  # Denmark's position among 49 countries
Y_DK = bg['Y'][:, k_DK * 7: (k_DK + 1)* 7].sum(1)  # Total final demand NL
BxL_DK = np.dot(bg['B'], bg['L'])  # Calculate multipliers/intensities/coefficients
R_ind = np.dot(BxL_DK, Y_DK)  # Indirect impacts from NL total final demand 

R_y = bg['H'][:, k_DK * 7: (k_DK + 1)* 7].sum(1)  # Direct impacts from NL total final demand 

R_ind = np.delete(R_ind, [4, 5])  # Remove value added and nr of employees 
R_y = np.delete(R_y, [4, 5])

# Combine healthcare footprint and national consumption footprint
share_hc = pd.concat([R_HC, pd.Series(data = np.add(R_y, R_ind), index = cols_impcat)], axis = 1)
share_hc.columns = ['Healthcare footprint', 'National consumption footprint']
share_hc['Healthcare share of national consumption footprint (%)'] = 100* share_hc['Healthcare footprint'] / share_hc['National consumption footprint']

# Read Table S5 to Excel file
share_hc.to_excel('table_s5_dk.xlsx')

#The following line is a sanity check for the country index
# print(bg['label']['region'].reset_index().iloc[k_DK])

# 7E) Contribution analysis (underlying data for Figure 1 and Table S6)
df_c_all = df_c[0][['ISO3','RegName', 'Region', 'SecTxtCode', 'SecName', 'SAggDescription', 'Scope'] + cols_impcat]
df_c_aggsec = df_c[0].groupby(['SAggDescription'])[cols_impcat].sum()
df_c_allsec = df_c[0].groupby(['SecTxtCode', 'SecName'])[cols_impcat].sum()

# coefficients/multipliers/intensities to csv for several aggregation levels
writer = pd.ExcelWriter(os.path.join(interim_dir, 'contribution_analysis.xlsx'),
                        engine='xlsxwriter')
df_c_all.to_excel(writer, sheet_name='full')
df_c_allsec.to_excel(writer, sheet_name='allsec')
df_c_aggsec.to_excel(writer, sheet_name='aggsec')
writer.close()

# Hotspot analysis (underlying data for Figure 2, 3 and Table S7, S8)
df_h_all = df_h[0][['ISO3','RegName', 'Region', 'SecTxtCode', 'SecName', 'SAggDescription', 'Scope'] + cols_impcat]
df_h_all.loc[df_h_all['ISO3']=='GLO', ['RegName', 'Region']] = 'Unallocated'

df_h_aggsec = df_h_all.groupby(['Scope','SAggDescription'])[cols_impcat].sum()
df_h_aggsec_aggreg = df_h_all.groupby(['Scope', 'RegName','SAggDescription'])[cols_impcat].sum()
df_h_aggreg = df_h_all.groupby(['Scope', 'Region', 'RegName'])[cols_impcat].sum()
df_h_allreg = df_h_all.groupby(['Scope', 'RegName'])[cols_impcat].sum()
df_h_allsec = df_h_all.groupby(['Scope', 'SecTxtCode', 'SecName'])[cols_impcat].sum()

writer = pd.ExcelWriter(os.path.join(interim_dir, 'hotspot_analysis.xlsx'),
                        engine='xlsxwriter')
df_h_all.to_excel(writer, sheet_name='full')
df_h_aggsec.to_excel(writer, sheet_name='aggsec')
df_h_aggsec_aggreg.to_excel(writer, sheet_name='aggsec_aggreg')
df_h_aggreg.to_excel(writer, sheet_name='aggreg')
df_h_allreg.to_excel(writer, sheet_name='allreg')
df_h_allsec.to_excel(writer, sheet_name='allsec')
writer.close()

# 7F) Calculate Scope 1, 2, 3 emissions for healthcare sector
# WARNING; it seems almost all MRIO emissions are categorised as SCope 2 and 3


# 7F) Scopes (GHG Protocol) for Denmark + separate Figure 4 (Scopes_Figure.pdf)
# -----------------------------------------------------------------------------------
# This block:
#   • Matches DK healthcare sectors  (Human health services + Residential care & social work).
#   • Computes Scope 1/2/3 in line with GHG Protocol.
#   • Adds bottom-up (anaesthetics and pMDI → S1; commuting and visitor → S3).
#   • Prints diagnostics.
#   • Saves a separate bar chart figure as Scopes_Figure.pdf (and PNG).

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Inputs from bg / earlier parts of the script ---
L = bg['L']
B = bg['B']            # Intensities matrix; row 0 is 'Global warming (ktCO2eq)' as per functions2025.py
Ystim = bg['Ystim']    # Column 0 = 'Tot' (Total expenditure vector)
labels_ind = bg['label']['industry']   # 163 sector names (one-region list)
labels_reg = bg['label']['region']     # 49 regions
ns = int(labels_ind.shape[0])          # 163
nr = int(labels_reg.shape[0])          # 49
N = ns * nr

# Reconstruct the full sector-name vector for all (region, sector) positions, ordered by region blocks.
sector_names_full = pd.Series(list(labels_ind['Name']) * nr, index=np.arange(N))

# Denmark region index 
k_DK = 6
start_DK, end_DK = k_DK * ns, (k_DK + 1) * ns
dk_sector_names = sector_names_full.iloc[start_DK:end_DK]

# --- Diagnostics: show DK block sector names (first 25) ---
print("\n[DIAG] First 25 sector names in the Denmark block:")
for i, nm in enumerate(dk_sector_names.head(25).tolist(), start=1):
    print(f"  {i:>2}. {nm}")

# --- Helper: find positions in a specific region block by exact or regex match ---
def find_positions_in_region(names_series: pd.Series,
                             region_start: int,
                             n_sectors: int,
                             exact_names=None,
                             regex_patterns=None):
    """
    Returns a list of integer positions (global index) in region block
    that match any exact_names OR any regex_patterns (case-insensitive).
    """
    exact_names = exact_names or []
    regex_patterns = regex_patterns or []
    sub = names_series.iloc[region_start:region_start + n_sectors]
    pos = []

    # 1) Exact-name priority (robust if EXIOBASE canonical names exist)
    lname_map = {nm.lower(): idx for idx, nm in zip(sub.index, sub.values)}
    for ex in exact_names:
        ex_l = ex.lower()
        if ex_l in lname_map:
            pos.append(lname_map[ex_l])

    # 2) Regex fallback
    if regex_patterns:
        mask = pd.Series(False, index=sub.index)
        for pat in regex_patterns:
            mask = mask | sub.str.contains(pat, case=False, regex=True, na=False)
        # Avoid duplicates
        for idx in mask[mask].index:
            if idx not in pos:
                pos.append(idx)

    return sorted(pos)

# --- GHG Protocol scopes, corrected construction -----------------------------------
# Scope 1 = direct emissions of the reporting scope (health + eldercare providers):
#           the DRIVHUS national-accounts figure (excl. medical N2O) computed above
#           and stored in dk_data_2025.csv / bg['Hstim'], plus the medical-gas
#           bottom-up items (anaesthetic gases; pMDIs are released at patients'
#           homes and are booked to Scope 3, following Steenmeijer et al. Table S8).
# Scope 2 = generation emissions of the electricity/steam/hot water purchased
#           DIRECTLY by the providers: first-tier energy purchases are the energy-
#           sector entries of the scaled intermediate-input column (Ystim col 1,
#           'HC'), and their generation emissions are those purchases times the
#           energy sectors' own direct emission intensity B. Upstream emissions of
#           the energy chain remain in Scope 3, as the GHG Protocol prescribes.
#           (The previous revision summed electricity/heat emissions over the WHOLE
#           supply chain, which mixes Scope 2 and 3; see revision notes.)
# Scope 3 = all remaining supply-chain emissions plus employee commuting.
# Patient/visitor travel = outside the GHG Protocol (reported separately).

gwp_idx = 0  # 'Global warming (ktCO2eq)' row in B
x_tot = L @ Ystim[:, 0]  # Total monetary outputs induced by total expenditure vector
emissions_mrio_total = float(B[gwp_idx, :] @ x_tot)  # kt CO2eq

elec_mask = sector_names_full.str.contains(r"\belectricity\b", case=False, regex=True, na=False)
heat_mask = sector_names_full.str.contains(r"\bsteam\b", case=False, regex=True, na=False) | \
            sector_names_full.str.contains(r"\bhot\s*water\b", case=False, regex=True, na=False)
energy_positions = np.where(elec_mask | heat_mask)[0]

# Direct operational emissions (DRIVHUS-based, kt CO2e) as carried in cbs_data.
scope1_direct = float(cbs_data.loc[('DirectEm', 'kt CO2e'), 'HC service'])

# Purchased energy of the providers (column 1 of Ystim = healthcare services
# component, i.e. the scaled Z-column of DK Health and social work). EXIOBASE
# books much of the purchase against transmission/distribution sectors whose own
# combustion emissions are ~0, with generation one tier upstream - so Scope 2 is
# obtained by tracing the purchased-energy demand through the Leontief inverse
# and collecting the emissions occurring IN energy sectors (generation);
# non-energy upstream emissions of the energy chain (fuel mining etc.) stay in
# Scope 3, per the GHG Protocol.
purchase_vec = np.zeros_like(Ystim[:, 1])
purchase_vec[energy_positions] = Ystim[energy_positions, 1]
x_energy_chain = L @ purchase_vec
scope2_generation = float(B[gwp_idx, energy_positions] @ x_energy_chain[energy_positions])

# --- Bottom-up additions ---
BU_path = BOTTOMUP_2025
BU_data_scopes = pd.read_csv(BU_path, sep='\t').set_index('Source')
BU_data_scopes = BU_data_scopes.drop(columns=['ISO2'], errors='ignore')

anaesthetic_kt = float(BU_data_scopes.loc['Anaesthetic', 'Global warming (ktCO2eq)'])
pmdi_kt       = float(BU_data_scopes.loc['pMDI', 'Global warming (ktCO2eq)'])
commute_kt    = float(BU_data_scopes.loc['Commute (total)', 'Global warming (ktCO2eq)'])
visitor_kt    = float(BU_data_scopes.loc['Visitor travel (total)', 'Global warming (ktCO2eq)'])

scope1_total = scope1_direct + anaesthetic_kt
scope2_total = scope2_generation
scope3_total = (emissions_mrio_total - scope2_generation) + pmdi_kt + commute_kt
outside_protocol = visitor_kt
total_footprint = scope1_total + scope2_total + scope3_total + outside_protocol

print("\n[CHECK] MRIO total (kt CO2eq) =", round(emissions_mrio_total, 2))
print(f"\nScope 1 direct (DRIVHUS, excl. medical N2O): {scope1_direct:.2f} kt CO2eq")
print(f"  + Anaesthetic gases (bottom-up)          : {anaesthetic_kt:.2f} kt CO2eq")
print(f"Scope 1 total                              : {scope1_total:.2f} kt CO2eq")
print(f"\nScope 2 (generation of purchased energy)   : {scope2_total:.2f} kt CO2eq")
print(f"\nScope 3 (supply chain incl. upstream energy): {emissions_mrio_total - scope2_generation:.2f} kt CO2eq")
print(f"  + pMDI (bottom-up, use phase)            : {pmdi_kt:.2f} kt CO2eq")
print(f"  + Commute (bottom-up)                    : {commute_kt:.2f} kt CO2eq")
print(f"Scope 3 total                              : {scope3_total:.2f} kt CO2eq")
print(f"\nOutside protocol (patient/visitor travel)  : {outside_protocol:.2f} kt CO2eq")
print(f"\nTotal healthcare footprint                 : {total_footprint:.2f} kt CO2eq")

# --- Figure 4: Scopes bar chart saved separately ---
scope_labels = ['Scope 1', 'Scope 2', 'Scope 3', 'Outside protocol']
scope_values = [scope1_total, scope2_total, scope3_total, outside_protocol]

fig_scope, ax_scope = plt.subplots(figsize=(6.5, 5.0))
bars = ax_scope.bar(scope_labels, scope_values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#7f7f7f'])
ax_scope.set_ylabel('kt CO₂eq')
ax_scope.set_title('Healthcare Footprint by Scope (DK, total)')
# Annotate bar tops
for bar, val in zip(bars, scope_values):
    ax_scope.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.01,
                  f"{val:.0f}", ha='center', va='bottom', fontsize=10)
plt.tight_layout()

# Save to separate files
plt.savefig('fig_scope.png', dpi=600)
fig_scope.savefig('scopes_figure.pdf')
plt.close(fig_scope)

print("fig_scope.png")
print("scopes_figure.pdf")
# -----------------------------------------------------------------------------------


# --- CSV export: Scopes summary (kt CO2eq) ---
scopes_rows = [
    {"Component": "Scope 1 direct (DRIVHUS, excl. medical N2O)", "kt_CO2eq": scope1_direct},
    {"Component": "  + Anaesthetic gases (bottom-up)",           "kt_CO2eq": anaesthetic_kt},
    {"Component": "Scope 1 (Total)",                             "kt_CO2eq": scope1_total},
    {"Component": "Scope 2 (generation of purchased energy)",    "kt_CO2eq": scope2_total},
    {"Component": "Scope 3 (MRIO supply chain excl. Scope 2)",   "kt_CO2eq": emissions_mrio_total - scope2_generation},
    {"Component": "  + pMDI (bottom-up, use phase)",             "kt_CO2eq": pmdi_kt},
    {"Component": "  + Commute (bottom-up)",                     "kt_CO2eq": commute_kt},
    {"Component": "Scope 3 (Total)",                             "kt_CO2eq": scope3_total},
    {"Component": "Outside protocol (patient/visitor travel)",   "kt_CO2eq": outside_protocol},
    {"Component": "Grand Total",                                 "kt_CO2eq": total_footprint},
]
scopes_df = pd.DataFrame(scopes_rows)
scopes_csv = os.path.join(output_dir, "scopes_summary.csv")
scopes_df.to_csv(scopes_csv, index=False)
print(f"Scopes summary written → {scopes_csv}")


print("\n[CHECK] dk_data_2025 DirectEm (kt CO2e) for HC service:",
      cbs_data.loc[('DirectEm', 'kt CO2e'), 'HC service'])

# 7G) plot figures (figures in manuscript are composed in MS Excel)
# Figure 1
fig_1 = pd.merge(df_c_aggsec.reset_index(), sec_labels[['SAggDescription','SAggCode']].drop_duplicates(), on = 'SAggDescription', how = 'left')
fig_1 = pd.merge(fig_1, fig_labels, on = 'SAggCode', how = 'left')

# Disaggregate Transport from 'Other'
fig_1['Contribution'] = fig_1['Contribution'].fillna('Unallocated')
fig_1.loc[fig_1['Contribution'] == 'Other', 'Contribution'] = 'Unallocated'
# Exact match: the substring test also captured 'Transport Equipment' (vehicle
# manufacturing), inflating the transport group.
mask_transport = fig_1['SAggDescription'].eq('Transport')
fig_1.loc[mask_transport, 'Contribution'] = 'Transport'

fig_1 = fig_1.groupby('Contribution')[cols_impcat].sum()

# Figure 2
fig_2 = pd.merge(df_h_aggsec.reset_index(), sec_labels[['SAggDescription','SAggCode']].drop_duplicates(), on = 'SAggDescription', how = 'left')
fig_2 = pd.merge(fig_2, fig_labels, on = 'SAggCode', how = 'left') 

fig_2 = pd.merge(df_h_aggsec.reset_index(),
                 sec_labels[['SAggDescription','SAggCode']].drop_duplicates(),
                 on='SAggDescription', how='left')
fig_2 = pd.merge(fig_2, fig_labels, on='SAggCode', how='left')

# Disaggregate Transport from 'Other' in hotspot (exact match, see fig_1 note)
fig_2['Hotspot'] = fig_2['Hotspot'].fillna('Unallocated')
fig_2.loc[fig_2['Hotspot'] == 'Other', 'Hotspot'] = 'Unallocated'
mask_transport = fig_2['SAggDescription'].eq('Transport')
fig_2.loc[mask_transport, 'Hotspot'] = 'Transport'

fig_2 = fig_2.groupby('Hotspot')[cols_impcat].sum()

# Figure 3
# Figure 3

fig3_temp = df_h_all.copy()
fig3_temp.loc[fig3_temp['RegName'] == 'Netherlands', 'Region'] = 'Europe'

fig_3 = fig3_temp.groupby(['Region'])[cols_impcat].sum()
fig_3 = fig_3.sort_index(ascending=False)

order = [x for x in fig_3.index if x != 'Denmark'] + ['Denmark']
fig_3 = fig_3.loc[order]

# ===============================
# EXPORT FULL RESULTS (Absolute values and percentages)
# ===============================

def create_relative(df):
    return df.apply(lambda col: 100 * col / col.sum(), axis=0)

# --- Absolute tables (raw results behind figures)
fig1_abs = fig_1.copy()
fig2_abs = fig_2.copy()
fig3_abs = fig_3.copy()

# --- Relative tables (percentage shares)
fig1_rel = create_relative(fig1_abs)
fig2_rel = create_relative(fig2_abs)
fig3_rel = create_relative(fig3_abs)

# ===============================
# SAVE CLEAN RESULT TABLES
# ===============================

writer = pd.ExcelWriter("full_results_tables.xlsx", engine="xlsxwriter")

# --- Contribution analysis (Figure 1)
fig1_abs.to_excel(writer, sheet_name="Fig1_absolute")
fig1_rel.to_excel(writer, sheet_name="Fig1_relative_%")

# --- Hotspot analysis (Figure 2)
fig2_abs.to_excel(writer, sheet_name="Fig2_absolute")
fig2_rel.to_excel(writer, sheet_name="Fig2_relative_%")

# --- Regional analysis (Figure 3)
fig3_abs.to_excel(writer, sheet_name="Fig3_absolute")
fig3_rel.to_excel(writer, sheet_name="Fig3_relative_%")

writer.close()

print("Full result tables exported: FullResults_Tables.xlsx")

# ===============================
# OPTIONAL: EXPORT FULL RAW DATA (HIGH RESOLUTION)
# ===============================

df_c_all.to_excel(os.path.join(interim_dir, 'contribution_full_detail.xlsx'))
df_h_all.to_excel(os.path.join(interim_dir, 'hotspot_full_detail.xlsx'))

print("Raw tables exported for full traceability")


# Plot and save figures
pdf_path = 'all_figures.pdf'
with PdfPages(pdf_path) as pdf:
    n = 1
    for df in [fig_1.sort_index(ascending=False), fig_2.sort_index(ascending=False), fig_3]:
        for col in df.columns:
            df[col] = 100 * df[col]/df[col].sum()
        ax = df.T.plot(kind='bar', stacked=True, colormap='tab10', figsize=(10, 6))
        plt.xticks(rotation=45, ha='right')
        handles, labels = ax.get_legend_handles_labels(); ax.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1.05, 1.0), loc='upper left')
        plt.xlabel("Impact category")
        plt.ylabel("Share of footprint")
        plt.tight_layout()
        png_name = f'fig_{n}.png'
        plt.savefig(png_name, dpi=600, bbox_inches='tight')
        pdf.savefig(ax.get_figure())
        plt.close()  # Close the figure to avoid popups and memory issues
        print(png_name)
        n += 1

print(f"All figures saved to {pdf_path}")

##############################################
# 8)  Diagnostics and additional checks
##############################################


# === Figure 5: (Diagnostics) Total contribution (MRIO + bottom-up), grouped like Figure 1,
# to double check that bottom up was included in the original script ===
# Start from MRIO aggregated contributions (fig_1 input, pre-group)
fig5_in = pd.merge(df_c_aggsec.reset_index(),
                   sec_labels[['SAggDescription','SAggCode']].drop_duplicates(),
                   on='SAggDescription', how='left')
fig5_in = pd.merge(fig5_in, fig_labels, on='SAggCode', how='left')
fig5_in['Contribution'] = fig5_in['Contribution'].fillna('Other')

# Bring in bottom-up totals across impact categories
BU5 = pd.read_csv(BOTTOMUP_2025, sep='\t').set_index('Source')

# Map bottom-up → Figure 1 groups (Dutch study: op. impacts + individual travel)
bu_op = BU5.loc[['Anaesthetic','pMDI'], cols_impcat].sum(axis=0) if all([x in BU5.index for x in ['Anaesthetic','pMDI']]) else fig5_in[cols_impcat].iloc[0]*0
bu_tr = BU5.loc[['Commute (total)','Visitor travel (total)'], cols_impcat].sum(axis=0) if all([x in BU5.index for x in ['Commute (total)','Visitor travel (total)']]) else fig5_in[cols_impcat].iloc[0]*0

# Append bottom-up rows to input (so they participate in the same grouping)
rows5 = []
rows5.append(pd.Series(['Bottom-up: Operational impacts','Operational impacts'] + list(bu_op.values),
                       index=['SAggDescription','Contribution']+cols_impcat))
rows5.append(pd.Series(['Bottom-up: Individual travel','Individual travel'] + list(bu_tr.values),
                       index=['SAggDescription','Contribution']+cols_impcat))
fig5_in = pd.concat([fig5_in, pd.DataFrame(rows5)], ignore_index=True)

# Optional: Disaggregate Transport from 'Other' (exact match, see fig_1 note)
mask_transport_c = fig5_in['SAggDescription'].eq('Transport')
fig5_in.loc[mask_transport_c, 'Contribution'] = 'Transport'

# Group and plot shares
fig5 = fig5_in.groupby('Contribution')[cols_impcat].sum()
fig5_share = fig5.apply(lambda col: 100*col/col.sum(), axis=0)

ax5 = fig5_share.T.plot(kind='bar', stacked=True, colormap='tab10', figsize=(10,6))
plt.xticks(rotation=45, ha='right')
plt.legend(bbox_to_anchor=(1.05,1.0), loc='upper left')
plt.xlabel("Impact category")
plt.ylabel("Share of total footprint")
plt.tight_layout()
plt.savefig('figure_5_total_contribution.png', dpi=600, bbox_inches='tight')
plt.close()
print("figure_5_total_contribution.png")



# 7H) Diagnostics for large 'Other' and Denmark share

print("\n[DIAG] Coverage of 'Contribution' mapping in fig_1 input:")
fig_1_in = pd.merge(df_c_aggsec.reset_index(),
                    sec_labels[['SAggDescription','SAggCode']].drop_duplicates(),
                    on='SAggDescription', how='left')
fig_1_in = pd.merge(fig_1_in, fig_labels, on='SAggCode', how='left')  # adds 'Contribution'
mapped = fig_1_in['Contribution'].notna().sum()
total = len(fig_1_in)
print(f"  mapped rows: {mapped}/{total} ({mapped/total:.1%}) have a named 'Contribution'")

print("\n[DIAG] Share by Contribution group (Global warming only):")
gwp_col = 'Global warming (ktCO2eq)'
share_by_group = (100 * fig_1_in.groupby('Contribution')[gwp_col].sum() /
                  fig_1_in[gwp_col].sum()).sort_values(ascending=False)
print(share_by_group)

# Drill into what's inside 'Other'
if 'Other' in share_by_group.index:
    print("\n[DIAG] Top 20 SAggDescription inside 'Other' (GWP):")
    other = fig_1_in[fig_1_in['Contribution'].fillna('Other') == 'Other']
    top_other = (other.groupby('SAggDescription')[gwp_col].sum()
                 .sort_values(ascending=False).head(20))
    print(top_other)


print("\n[DIAG] Expenditure shares from DK SUT (MEUR):")
bp_HCserv = float(cbs_data.iloc[0, 0])
bp_pharm  = float(cbs_data.iloc[0, 1]) * float(cbs_data.iloc[1, 1])  # conv=1.0 expected
bp_appl   = float(cbs_data.iloc[0, 2]) * float(cbs_data.iloc[1, 2])
tot_meur  = bp_HCserv + bp_pharm + bp_appl
print(f"  HC services: {bp_HCserv:.0f} MEUR ({100*bp_HCserv/tot_meur:.1f}%)")
print(f"  Pharma     : {bp_pharm:.0f} MEUR ({100*bp_pharm/tot_meur:.1f}%)")
print(f"  Appliances : {bp_appl:.0f} MEUR ({100*bp_appl/tot_meur:.1f}%)")

# Verify sector indices used in createBackground()
inds = bg['label']['industry'].reset_index(drop=True)
print("\n[DIAG] Sector name checks for hardcoded indices (should match EXIOBASE v3.7):")
for idx in [62, 89, 137]:
    if 0 <= idx < len(inds):
        print(f"  idx {idx:>3}: {inds.loc[idx, 'Name']}")
    else:
        print(f"  idx {idx:>3}: OUT OF RANGE")

# Contribution share for 'Pharmaceuticals and chemical products' (GWP)

print("[CHECK] Healthcare services expenditure (MEUR):", bp_HCserv)
print("[CHECK] Total scaled intermediate inputs (MEUR):", Ystim[:,0].sum())
print("[CHECK] Implied intermediate share (%):", 100 * Ystim[:,0].sum() / bp_HCserv)



k_health = 137
x_tot = bg['L'] @ bg['Ystim'][:, 0]
print(x_tot[k_DK*ns + k_health])


print("\n[DIAG] Top 15 intermediate-use sectors for DK healthcare (scaled):")
Ystim_df = pd.DataFrame(bg['Ystim'][:, 0], index=pd.MultiIndex.from_product(
    [bg['label']['region']['ISO3'], bg['label']['industry']['Name']]), columns=['MEUR'])
dk_block = Ystim_df.loc['DNK']
print(dk_block.sort_values('MEUR', ascending=False).head(15))

x_tot = bg['L'] @ bg['Ystim'][:, 0]
x_diag = np.diag(x_tot.astype(float))
Z_diag = bg['A'] @ x_diag  # shape: (ns*nr, ns*nr)
ns_ = bg['label']['industry'].shape[0]
nr = bg['label']['region'].shape[0]
names_ = list(bg['label']['industry']['Name'])


assert Z_diag.shape == (ns_ * nr, ns_ * nr)
assert len(names_) == ns_


# Slice DK and NL blocks (163 rows each)

if 'k_NL' not in globals():
    k_NL = list(bg['label']['region']['ISO3']).index('NLD')

start_DK, end_DK = k_DK*ns_, (k_DK+1)*ns_
start_NL, end_NL = k_NL*ns_, (k_NL+1)*ns_

col_DK = pd.Series(Z_diag[start_DK:end_DK, k_DK*ns_ + 137], index=names_, name='DK_HSW_Z')
col_NL = pd.Series(Z_diag[start_NL:end_NL, k_NL*ns_ + 137], index=names_, name='NL_HSW_Z')

# Compare DK vs NL 'Health & social work' columns (index 137 checked above)
ns_ = bg['label']['industry'].shape[0]
names_ = list(bg['label']['industry']['Name'])
k_DK = 6
k_NL = list(bg['label']['region']['ISO3']).index('NLD')


j_DK = k_DK * ns_ + 137
j_NL = k_NL * ns_ + 137

start_DK, end_DK = k_DK * ns_, (k_DK + 1) * ns_
start_NL, end_NL = k_NL * ns_, (k_NL + 1) * ns_

col_DK = pd.Series(
    Z_diag[start_DK:end_DK, j_DK],
    index=names_,
    name='DK_HSW_Z'
)

col_NL = pd.Series(
    Z_diag[start_NL:end_NL, j_NL],
    index=names_,
    name='NL_HSW_Z'
)

col_DK_global = pd.Series(
    Z_diag[:, j_DK].reshape(nr, ns_).sum(axis=0),
    index=names_,
    name='Global_to_DK_HSW_Z'
)


print("\n[DIAG] DK Health&SocialWork column (Z) top-12 by MEUR:")
print(col_DK.sort_values(ascending=False).head(12))


# Diagnostic: group-level intensity (kt CO2e per MEUR) for MRIO
g_int = (mult_aggsec[['Global warming (ktCO2eq)/MEUR']]
         .rename(columns={'Global warming (ktCO2eq)/MEUR':'ktCO2e_per_MEUR'}))
print("\n[DIAG] Group intensities (kt CO2e/MEUR), top 10:")
print(g_int.sort_values('ktCO2e_per_MEUR', ascending=False).head(10))

# === EXTRA: Resolve pharma/chemical group intensity robustly, and print Chemicals nec sector intensity ===
def _norm_label(s: str) -> str:
    return (str(s).strip().lower().replace('&', 'and').replace('  ', ' '))

gwp_int_col = 'Global warming (ktCO2eq)/MEUR'

# 1) Pharma/chemical aggregated group intensity (robust lookup in mult_aggsec)
_mult_aggsec_norm = mult_aggsec.copy()
_mult_aggsec_norm.index = pd.Index([_norm_label(ix) for ix in _mult_aggsec_norm.index], name='SAggDescription_norm')

# Find candidates whose normalized label contains 'pharm' or 'chemical'
_candidates = [ix for ix in _mult_aggsec_norm.index if ('pharm' in ix) or ('chemical' in ix)]
if _candidates := _candidates:  # Python 3.8+ walrus-safe; falls back to simple truthy check
    # If multiple, pick the one with highest intensity (defensive)
    _best_key = max(_candidates, key=lambda k: float(_mult_aggsec_norm.loc[k, gwp_int_col]))
    # Recover pretty original label from the un-normalized index of mult_aggsec
    # (by matching normalized strings back to the original)
    _orig_label = None
    for orig in mult_aggsec.index:
        if _norm_label(orig) == _best_key:
            _orig_label = orig
            break
    _pharma_int = float(_mult_aggsec_norm.loc[_best_key, gwp_int_col])

    print(f"\n[DIAG] Pharma/chemical group resolved as: '{_orig_label or _best_key}'")
    print(f"[DIAG] Intensity for pharma/chemical group: {_pharma_int:.3f} kt CO2e/MEUR")
else:
    print("\n[DIAG] Pharma/chemical group intensity: not found (check aggregation labels).")

# 2) Chemicals nec sector intensity (single EXIOBASE sector from mult_allsec)
_mult_allsec_norm = mult_allsec.copy()
_mult_allsec_norm.index = pd.Index([_norm_label(ix) for ix in _mult_allsec_norm.index], name='SecName_norm')

if 'chemicals nec' in _mult_allsec_norm.index:
    _chemnec_int = float(_mult_allsec_norm.loc['chemicals nec', gwp_int_col])
    # Recover pretty original sector name for the printout
    _chemnec_pretty = None
    for orig in mult_allsec.index:
        if _norm_label(orig) == 'chemicals nec':
            _chemnec_pretty = orig
            break
    print(f"[DIAG] Intensity for '{_chemnec_pretty or 'Chemicals nec'}': {_chemnec_int:.3f} kt CO2e/MEUR")
else:
    print("[DIAG] 'Chemicals nec' sector not found in mult_allsec (check sector naming).")


# Diagnostic: transport emissions by region

transport_mask = sector_names_full.str.contains('Transport', case=False, na=False)
transport_emissions_by_region = pd.Series(0.0, index=list(bg['label']['region']['ISO3']))

for r in range(nr):
    start, end = r * ns_, (r + 1) * ns_
    sel = np.array(transport_mask[start:end])
    if sel.any():
        transport_emissions_by_region.iloc[r] = float(
            B[0, start:end][sel] @ x_tot[start:end][sel]
        )

print("\n[DIAG] Transport emissions by region (kt CO2eq):")
print(transport_emissions_by_region.sort_values(ascending=False))


# === PATCH: Robust resolution of the pharma/chemical aggregated group ===
def _norm_label(x: str) -> str:
    return (str(x)
            .strip()
            .lower()
            .replace('&', 'and')
            .replace('  ', ' '))

gwp_col = 'Global warming (ktCO2eq)'

# Build a normalized index copy for robust lookup, preserving original labels
_df_c_aggsec_norm = df_c_aggsec.copy()
_df_c_aggsec_norm.index = pd.Index([_norm_label(s) for s in df_c_aggsec.index], name='SAggDescription_norm')

# Candidates whose normalized label contains 'pharm' or 'chemical'
_candidates = [k for k in _df_c_aggsec_norm.index if ('pharm' in k) or ('chemical' in k)]

if _candidates:
    # Pick the candidate with the largest GWP (most representative if multiple exist)
    _best_key = max(_candidates, key=lambda k: float(_df_c_aggsec_norm.loc[k, gwp_col]))
    # Recover the original human-readable label that corresponds to the normalized key
    _orig_label = df_c_aggsec.index[_df_c_aggsec_norm.index.get_loc(_best_key)]
    _share = 100.0 * float(_df_c_aggsec_norm.loc[_best_key, gwp_col]) / float(df_c_aggsec[gwp_col].sum())

    print(f"\n[DIAG] Pharma/chemical group resolved as: '{_orig_label}'")
    print(f"[DIAG] GWP share for '{_orig_label}': {_share:.1f}%")



# Optional: confirm that 'Chemicals nec' appears in the pharma/chem breakdown
inds_chk = bg['label']['industry'].reset_index(drop=True)
print("\n[DIAG] Sector @ index 62:", inds_chk.loc[62, 'Name'] if 62 < len(inds_chk) else 'index 62 out of range')


# === Audit: what goes into DK 'Other land transport' (inputs per euro of output)?
# Find DK region index and the local sector index for 'Other land transport'
k_DK = list(bg['label']['region']['ISO3']).index('DNK')
ns_  = int(bg['label']['industry'].shape[0])
nr   = int(bg['label']['region'].shape[0])

sector_names = list(bg['label']['industry']['Name'])
sector_names_full = pd.Series(sector_names * nr)  # (ns*nr,)

# Robust find of the sector position within a region
def _find_pos_in_region(names_series, region_idx, ns, pattern_regex):
    start, end = region_idx*ns, (region_idx+1)*ns
    sub = names_series.iloc[start:end]
    hit = sub[sub.str.contains(pattern_regex, case=False, regex=True, na=False)]
    if hit.empty:
        return None
    return hit.index[0]

# Try typical EXIOBASE label 'Other land transport'
j_local = _find_pos_in_region(sector_names_full, k_DK, ns_, r"\bother\s+land\s+transport\b")
if j_local is None:
    raise ValueError("Could not find 'Other land transport' in DK block; check sector names.")
j_DK_OLT = j_local  # absolute index in (ns*nr,)

# Column of A for DK 'Other land transport' (input coefficients per euro output)
A_col = bg['A'][:, j_DK_OLT]  # shape (ns*nr,)

# (a) DK-only suppliers to DK OLT (length 163)
start_DK, end_DK = k_DK*ns_, (k_DK+1)*ns_
inputs_DK_only = pd.Series(A_col[start_DK:end_DK], index=sector_names, name='coeff_per_euro')
print("\n[DIAG] Inputs to DK Other land transport (DK suppliers only), top 20 by coefficient:")
print(inputs_DK_only.sort_values(ascending=False).head(20))

# (b) Global-by-sector suppliers to DK OLT (sum across 49 regions into 163 sectors)
inputs_global_by_sector = pd.Series(A_col.reshape(nr, ns_).sum(axis=0), index=sector_names, name='coeff_per_euro')
print("\n[DIAG] Inputs to DK Other land transport (GLOBAL, aggregated by sector), top 20:")
print(inputs_global_by_sector.sort_values(ascending=False).head(20))

# The following is a chunk of code that will produce an excel sheet with all the results for a table in the article


# ============================================================
# STEENMEIJER-STYLE TABLE EXPORT 
# ============================================================

# --- Rename columns to match terminology ---
t1_formatted = t1.rename(columns={
    'Expenditure (MEUR)': 'Basic price expenditure (million euros)',
    'Global warming (ktCO2eq)': 'Climate change (kt CO2eq)',
    'Material extraction (kt)': 'Material extraction (kt)',
    'Blue water consumption (Mm3)': 'Blue water consumption (Mm3)',
    'Land use (km2)': 'Land use (km2)',
    'Waste generation (kt)': 'Waste generation (kt)'
})

# --- Convert everything to numeric (safe) ---
for col in t1_formatted.columns:
    t1_formatted[col] = pd.to_numeric(t1_formatted[col], errors='coerce')

# --- Totals row (used for percentages) ---
totals = t1_formatted.iloc[0]

# --- Formatting function  ---
def format_val(val, total):
    if pd.isna(val):
        return "NA"
    if total == 0 or pd.isna(total):
        return f"{val:,.0f} (0.0%)"
    
    pct = 100 * val / total

    # Handle very small values like in paper
    if pct < 0.1:
        return f"{val:,.0f} (<0.1%)".replace('.', '·')
    
    return f"{val:,.0f} ({pct:.1f}%)".replace('.', '·')

# --- Apply formatting ---
t1_display = t1_formatted.copy().astype(object)  # string cells replace floats

for col in t1_formatted.columns:
    for i in range(len(t1_formatted)):
        t1_display.iloc[i, t1_display.columns.get_loc(col)] = format_val(
            t1_formatted.iloc[i][col],
            totals[col]
        )

# --- Add grouping column (like paper) ---
t1_display.insert(0, "Category group", [
    "Total",
    "Top-down",
    "Top-down",
    "Top-down",
    "Bottom-up",
    "Bottom-up",
    "Bottom-up"
])

# --- (Optional) Rename index to cleaner labels ---
t1_display.index = [
    "Total",
    "Health-care services",
    "Pharmaceuticals and chemical products",
    "Medical appliances",
    "Release of anaesthetic gases",
    "Release of pMDI propellants",
    "Private travel"
]

# --- Export to Excel ---
output_path = os.path.join(output_dir, "steenmeijer_table.xlsx")

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    t1_display.to_excel(writer, sheet_name='Table')

print(f"Steenmeijer-style table exported to: {output_path}")
