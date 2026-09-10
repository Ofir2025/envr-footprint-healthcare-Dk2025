# -*- coding: utf-8 -*-
"""Bridge EXIOBASE's 163 industries onto Statistics Denmark's 117 industries.

Motivation
----------
The simplified-SNAC coupling of Palm et al. (2019), specified in
``docs/methods/methods.md`` (section "Simplified SNAC, EXIOBASE coupling and
Danish healthcare footprint accounting") and scoped for Denmark in the same
file's "Danish SNAC" section, keeps the Danish national
input-output table as the authoritative domestic core and uses EXIOBASE only
for imports, evaluated as ``e_m = Q K m``. ``K`` needs a sector bridge between
the Danish DB07/NACE rev.2 classification the import vector ``m`` is written in
and the EXIOBASE region-industry nodes ``Q`` is written in. No such bridge
existed in this repository; this module builds one and tests it.

How the bridge was built
------------------------
Three sources, in order of authority:

1. **The EXIOBASE developers' own NACE rev.2 concordance**, ``Sheet3`` of
   ``NACE2full_EXIOBASEp.xlsx`` in the EXIOBASE developer concordance folder
   (see ``DEVELOPER_SOURCE``). It lists, for every NACE rev.2 code at levels 1
   to 4, the EXIOBASE industries that code maps to. Inverted and aggregated to
   the division, it gives each EXIOBASE industry its candidate NACE rev.2
   divisions; those candidate sets are frozen into ``DEVELOPER_NACE2`` so the
   module does not depend on a file outside the repository. Because the
   inversion is many-to-many, a candidate set is wider than the industry's
   principal activity: ``MACH`` carries 33 and 95 because NACE rev.2 moved
   repair out of the manufacturing divisions, not because machinery is repair.
2. **The ISIC rev.3 division** carried by EXIOBASE's own ``Code1`` (``i15.a``
   is ISIC 15, ``i90.5.f`` is ISIC 90). ISIC rev.3 divisions are identical to
   NACE rev.1.1 divisions, so this fixes the pre-2008 side of every mapping and
   is cross-checked against ``exiobase_industry_to_isic_rev3.csv``.
3. **The EXIOBASE industry description and the DST industry name**, which
   resolve the divisions that split or merge between the revisions: ISIC 15
   food into NACE 10/11, ISIC 24 into NACE 20/21, ISIC 22 into NACE 18/58/59,
   ISIC 33 into NACE 26/32, ISIC 72 into NACE 58/62/63, ISIC 74 into NACE
   69-82 and ISIC 85 into NACE 75/86/87/88.

``vintage_defect_audit.CONCORDANCE`` - twelve hand-built groups whose mapping
its author judged unambiguous - is the correctness anchor. The validation
asserts that every prefix of every seed group survives in this concordance;
where this concordance adds a division the seed omitted (post to NACE 53
alongside telecoms, veterinary to NACE 75 alongside human health, medical and
dental instruments to NACE 32.5 alongside 26) the seed group is reported as
``refined`` and both ratios are given, so the seed's own numbers stay
reproducible.

The split weights
-----------------
A one-to-many row divides one EXIOBASE industry between several Danish
industries, and until those shares are given the bridge is a binary incidence
matrix rather than the weighted ``K`` of ``e_m = Q K m``. That is not a neutral
default: the Danish industries inside a split can differ in emission intensity
by more than an order of magnitude, so an implementer who averages gets a
different answer from one who weights. Two share vectors are written out, both
from the published Danish table, both summing to one across the row:

``dst_import_share``
    Shares of Danish total imports of the row's products, the ``Total`` column
    of the workbook's ``Imports`` block. This is the vector a SNAC import
    estimate multiplies, so it is the sharpest reading of ``K`` and the one
    this module recommends, with one caveat recorded in
    :func:`split_sensitivity`: a barely traded group rests its shares on a
    small base and is better weighted on output.
``dst_output_share``
    Shares of Danish output, the production-share proxy of Palm et al. (2019),
    kept because it is the published convention and because it is defined for
    every row.

Where the weights are and are not needed. The Danish table publishes imports by
product at the same 117-industry resolution as the emission accounts, so an
implementer who keeps the import vector in Danish classification applies ``Q``
directly and needs no split weights at all. The weights are needed when the
import vector arrives in EXIOBASE classification, which is the case here
because the healthcare demand vector is defined on EXIOBASE products, and when
a Danish-technology estimate has to be attributed back onto EXIOBASE nodes for
comparison with the model result. A module that holds its own ``m`` should
weight by that vector rather than by either default written here.

``snac_split_weight_sensitivity.csv`` reports what the choice costs. In 2022
thirteen of the twenty-nine splits move their intensity by more than a quarter
between the two, and the two largest by imported footprint move most: chemicals
because Danish output is three-quarters pharmaceutical while Danish imports are
only half, and the crude oil group because oil and gas extraction is fifty-five
times as emission-intensive as mining support.

Declared gaps
-------------
Nine EXIOBASE industries have no DST counterpart: the eight metal-ore mining
industries, because NACE rev.2 division 07 has no industry in the DST 117
grouping, and extra-territorial bodies (NACE 99). An unmatched EXIOBASE
industry costs a SNAC implementer nothing directly, since ``K`` is indexed on
the Danish side; the one gap that does bite runs the other way. DST 330000,
repair and installation of machinery and equipment, has no EXIOBASE source at
all: NACE rev.2 created division 33 out of repair activities that ISIC rev.3
kept inside manufacturing divisions 29 to 35, so no single EXIOBASE industry
corresponds and this module refuses to pick one.

Reading the confidence column
-----------------------------
``high``   the correspondence is documented and the industry's principal
           activity maps wholly onto the named DST industries.
``medium`` an EXIOBASE hybrid waste or re-processing activity with no DST
           industry of its own, or a split this module had to resolve by
           judgement.
``low``    no Danish activity exists, so the assignment rests on the
           classification alone.
For an ``unmatched`` row the confidence is the confidence that no DST
counterpart exists, not the confidence of a match.

What the validation cannot do, and the two controls it uses instead
-------------------------------------------------------------------
An output comparison tests a mapping only up to the difference between the two
databases. EXIOBASE's Danish block is known to misallocate output between
industries (Rørmose Jensen & Iliev 2022; ``vintage_defect_audit``), so a
flagged group is evidence of either a mapping error or a database defect and a
ratio on its own cannot separate them. Two controls are built in.

*The seed groups.* Twelve groups whose mapping an independent hand-built
concordance judged unambiguous. A flag on one of those is inherited, not
introduced here.

*Two years.* Both years are validated. The v3.8.2 distribution's own
``metadata.json`` shows every year of the release, 2016 and 2022 alike, written
in September 2021, so its 2022 table is a projection: it cannot know the 2022
energy-price and container-freight booms that the Danish national accounts
record. EXIOBASE Danish total output is 104 % of the national-accounts total
in 2016 and 84 % in 2022, so a group ratio is read against its own year's
aggregate (the ``ratio_relative_to_national_aggregate`` column), and a group
that is sound in 2016 and flagged in 2022 is a nowcast artefact rather than a
mapping error.

Run
---
``PYTHONPATH=src HC_ANALYSIS_YEAR=2022 .venv/bin/python -m
analysis.build_dst_concordance``
"""

from __future__ import annotations

import re
from typing import Iterable

import numpy as np
import pandas as pd

from analysis.constants import ANALYSIS_YEAR, K_DK, N_SECTORS
from analysis.vintage_defect_audit import CONCORDANCE as SEED_CONCORDANCE
from paths import BRONZE_DIR, EXIOBASE_DIR, OUTPUT_DIR

FOLDER = "06_benchmarks_validation"
CONCORDANCE_CSV = (BRONZE_DIR / "concordances"
                   / "exiobase_industry_to_dst_db07.csv")
VALIDATION_CSV = "dst_concordance_validation.csv"
ISIC_CSV = BRONZE_DIR / "concordances" / "exiobase_industry_to_isic_rev3.csv"
CLASSIFICATIONS = EXIOBASE_DIR / "classifications.xlsx"
DST_IO = (BRONZE_DIR / "input_output" / "2016_2022"
          / "input_output_en_{year}.xlsx")
EXIOBASE_X = EXIOBASE_DIR / "IOT_{year}_ixi" / "x.txt"
SATELLITE_CSV = BRONZE_DIR / "dst_emission_accounts_by_industry.csv"
SENSITIVITY_CSV = "snac_split_weight_sensitivity.csv"

#: Years the split-weight sensitivity is reported for. Both are years of
#: this study and both are covered by the DST satellite; 2016 is not.
WEIGHT_YEARS = ("2019", "2022")

#: Danish crowns per euro, annual average, used for the DST workbook.
DKK_PER_EUR = {"2016": 7.4452, "2022": 7.4396}

#: A group whose two output totals differ by more than this factor is flagged.
FLAG_FACTOR = 2.0

#: Years validated. 2016 is the control: it is a genuine EXIOBASE reference
#: year, where the 2022 table of the same release is a projection.
CONTROL_YEAR = "2016"

DEVELOPER_SOURCE = (
    "EXIOBASE developers' NACE rev.2 concordance, NACE2full_EXIOBASEp.xlsx "
    "Sheet3, from the EXIOBASE developer concordance set "
    "(mrio/classifications/concordances/exiobase/developers_concordances); "
    "NACE rev.2 codes at levels 1-4 against EXIOBASE industry names, inverted "
    "here and aggregated to the two-digit division"
)

#: Candidate NACE rev.2 divisions per EXIOBASE industry, from the developers'
#: concordance inverted to the division. Evidence, not the mapping: the
#: inversion is many-to-many, so these sets are wider than the industry's
#: principal activity. Empty where the developers' table has no entry.
DEVELOPER_NACE2: dict[str, str] = {
    "PARI": "01", "WHEA": "01", "OCER": "01", "FVEG": "01", "OILS": "01",
    "SUGB": "01", "FIBR": "01", "OTCR": "01", "CATL": "01", "PIGS": "01",
    "PLTR": "01", "OMEA": "01", "OANP": "01", "MILK": "01", "WOOL": "01",
    "MANC": "01", "MANB": "01", "FORE": "02", "FISH": "03", "COAL": "05 08 09",
    "COIL": "06 09", "GASE": "06 09", "OGPL": "06 09", "ORAN": "07 09",
    "IRON": "07 09", "COPO": "07 09", "NIKO": "07 09", "ALUO": "07 09",
    "PREO": "07 09", "LZTO": "07 09", "ONFO": "07 09", "STON": "08 09",
    "SDCL": "08 09", "CHMF": "08 09", "PCAT": "10", "PPIG": "10", "PPLT": "10",
    "POME": "10", "VOIL": "10", "DAIR": "10", "RICE": "10", "SUGR": "10",
    "OFOD": "10", "BEVR": "11", "FSHP": "10", "TOBC": "12", "TEXT": "13 14",
    "GARM": "14", "LETH": "15", "WOOD": "16", "WOOW": "16", "PULP": "17",
    "PAPR": "17", "PAPE": "17", "MDIA": "18 58 59", "COKE": "19", "REFN": "19",
    "NUCF": "24", "PLAS": "20", "PLAW": "20", "NFER": "20", "PFER": "20",
    "CHEM": "20 21", "RUBP": "22", "GLAS": "23", "GLAW": "", "CRMC": "23",
    "BRIK": "23", "CMNT": "23", "ASHW": "", "ONMM": "23", "STEL": "24",
    "STEW": "24", "PREM": "24", "PREW": "24", "ALUM": "24", "ALUW": "24",
    "LZTP": "24", "LZTW": "24", "COPP": "24", "COPW": "24", "ONFM": "24",
    "ONFW": "24", "METC": "24", "FABM": "25 33", "MACH": "25 27 28 33 95",
    "OFMA": "26 28 33", "ELMA": "26 27 28 29 33", "RATV": "26 27 28 33 95",
    "MEIN": "26 28 32 33", "MOTO": "29 30", "OTRE": "28 30 33",
    "FURN": "26 31 32 33 95", "RYMS": "38", "BOTW": "38", "POWC": "35",
    "POWG": "35", "POWN": "35", "POWH": "35", "POWW": "35", "POWP": "35",
    "POWB": "35", "POWS": "35", "POWE": "35", "POWO": "35", "POWM": "35",
    "POWZ": "35", "POWT": "35", "POWD": "35", "GASD": "35", "HWAT": "35",
    "WATR": "36", "CONS": "41 42 43", "CONW": "41 42 43", "TDMO": "45",
    "TDFU": "", "TDWH": "46", "TDRT": "47 95", "HORE": "55 56", "TRAI": "49",
    "TLND": "49", "TPIP": "49", "TWAS": "50", "TWAI": "50", "TAIR": "51",
    "TAUX": "52 79", "PTEL": "53 61", "FINT": "64", "FINS": "65", "FAUX": "66",
    "REAL": "68", "MARE": "77", "COMP": "58 62 63 95", "RESD": "72",
    "OBUS": "63 64 69 70 71 73 74 77 78 80 81 82 85", "PADF": "84",
    "EDUC": "85", "HEAL": "75 86 87 88", "INCF": "38 39", "INCP": "38 39",
    "INCL": "38 39", "INCM": "38 39", "INCT": "38 39", "INCW": "38 39",
    "INCO": "38 39", "BIOF": "38 39", "BIOP": "38 39", "BIOS": "38 39",
    "COMF": "38 39", "COMW": "38 39", "WASF": "37", "WASO": "37",
    "LANF": "38 39", "LANP": "38 39", "LANL": "38 39", "LANI": "38 39",
    "LANT": "38 39", "LANW": "38 39", "ORGA": "94",
    "RECR": "59 60 63 79 90 91 92 93", "OSER": "93 96", "PRHH": "97 98",
    "EXTO": "99",
}

_POW = ("POWC", "POWG", "POWN", "POWH", "POWW", "POWP", "POWB", "POWS",
        "POWE", "POWO", "POWM", "POWZ", "POWT", "POWD")
_WASTE_TREATMENT = ("INCF", "INCP", "INCL", "INCM", "INCT", "INCW", "INCO",
                    "BIOF", "BIOP", "BIOS", "COMF", "COMW",
                    "LANF", "LANP", "LANL", "LANI", "LANT", "LANW")

#: The concordance itself: EXIOBASE industry codes -> DST 117-industry codes,
#: with the confidence and basis of each decision. An empty DST string means
#: no Danish counterpart exists. Every one of the 163 industries appears once;
#: ``build_concordance`` asserts it.
MAPPING: list[tuple[tuple[str, ...], str, str, str]] = [
    # --- agriculture, forestry, fishing ---------------------------------
    (("PARI", "WHEA", "OCER", "FVEG", "OILS", "SUGB", "FIBR", "OTCR", "CATL",
      "PIGS", "PLTR", "OMEA", "OANP", "MILK", "WOOL"), "010000", "high",
     "ISIC rev.3 01 = NACE rev.2 01, developer table 01; DST has a single "
     "NACE 01 industry so all fifteen crop and livestock activities collapse"),
    (("MANC", "MANB"), "010000", "medium",
     "EXIOBASE hybrid manure-treatment activity, developer table 01; DST has "
     "no manure industry, the activity sits inside 010000"),
    (("FORE",), "020000", "high", "ISIC rev.3 02 = NACE rev.2 02"),
    (("FISH",), "030000", "high", "ISIC rev.3 05 -> NACE rev.2 03"),
    # --- mining and quarrying -------------------------------------------
    (("COAL",), "080090", "medium",
     "developer table 05 08 09; NACE rev.2 05 coal and lignite has no DST "
     "117 industry, only the peat component NACE 08.92 does, so the match "
     "covers part of the industry"),
    (("COIL", "GASE", "OGPL"), "060000;090000", "high",
     "developer table 06 09; ISIC rev.3 11 bundles extraction with the "
     "incidental services NACE rev.2 moved to 09.1 = DST 090000"),
    (("ORAN", "IRON", "COPO", "NIKO", "ALUO", "PREO", "LZTO", "ONFO"), "",
     "high",
     "developer table 07 09; NACE rev.2 division 07 mining of metal ores has "
     "no industry in the DST 117 grouping, Denmark mines no metal ore"),
    (("STON", "SDCL", "CHMF"), "080090", "high",
     "developer table 08 09; the DST name 'Extraction of gravel and stone' "
     "is NACE rev.2 08"),
    # --- food, beverages, tobacco ---------------------------------------
    (("PCAT", "PPIG", "PPLT", "POME"), "100010", "high",
     "NACE rev.2 10.1, DST 'Production of meat and meat products'"),
    (("FSHP",), "100020", "high",
     "NACE rev.2 10.2, DST 'Processing and preserving of fish'"),
    (("DAIR",), "100030", "high", "NACE rev.2 10.5, DST dairy products"),
    (("RICE",), "100040", "high",
     "NACE rev.2 10.61 grain milling, DST 'grain mill and bakery products'"),
    (("VOIL",), "100050", "high",
     "NACE rev.2 10.4 oils and fats, DST other manufacture of food "
     "products"),
    (("SUGR",), "100050", "high",
     "NACE rev.2 10.81 sugar, DST 'Other manufacture of food products'"),
    (("OFOD",), "100040;100050", "medium",
     "residual food industry: NACE rev.2 10.3 and 10.6-10.9 straddle the DST "
     "grain-mill/bakery and other-food split, so a weight is needed"),
    (("BEVR",), "110000", "high", "developer table 11, ISIC rev.3 15.5"),
    (("TOBC",), "120000", "high", "ISIC rev.3 16 = NACE rev.2 12"),
    # --- textiles, wood, paper, media -----------------------------------
    (("TEXT",), "130000", "high",
     "ISIC rev.3 17 -> NACE rev.2 13; the developer table also lists 14 for "
     "knitted apparel NACE 14.3, which GARM covers"),
    (("GARM",), "140000", "high", "ISIC rev.3 18 -> NACE rev.2 14"),
    (("LETH",), "150000", "high", "ISIC rev.3 19 -> NACE rev.2 15"),
    (("WOOD",), "160000", "high", "ISIC rev.3 20 -> NACE rev.2 16"),
    (("WOOW",), "160000", "medium",
     "EXIOBASE hybrid wood re-processing, developer table 16; NACE rev.2 "
     "would place materials recovery in 38.32, DST separates neither"),
    (("PULP", "PAPE"), "170000", "high", "ISIC rev.3 21 -> NACE rev.2 17"),
    (("PAPR",), "170000", "medium",
     "EXIOBASE hybrid paper re-processing, developer table 17"),
    (("MDIA",), "180000;580010;590000", "medium",
     "ISIC rev.3 22 splits in NACE rev.2 into 18 printing, 58.1 book and news "
     "publishing and 59.2 sound recording, developer table 18 58 59; software "
     "publishing NACE 58.2 came from ISIC 72 and is left to COMP"),
    # --- coke, refining, chemicals, rubber ------------------------------
    (("COKE", "REFN"), "190000", "high",
     "ISIC rev.3 23.1 and 23.2 -> NACE rev.2 19, DST 'Oil refinery etc.'"),
    (("NUCF",), "240000", "low",
     "developer table 24: NACE rev.2 places processing of nuclear fuel in "
     "24.46; there is no Danish activity, so the assignment rests on the "
     "classification alone"),
    (("PLAS", "NFER", "PFER"), "200010", "high",
     "developer table 20, NACE rev.2 20.15-20.16, DST 'basic chemicals'"),
    (("PLAW",), "200010", "medium",
     "EXIOBASE hybrid plastic re-processing, developer table 20"),
    (("CHEM",), "200010;200020;210000", "high",
     "developer table 20 21: the EXIOBASE residual chemical industry is the "
     "only source for DST pharmaceuticals 210000 and paints and soap 200020, "
     "which is the pharma-proxy problem this study documents"),
    (("RUBP",), "220000", "high", "ISIC rev.3 25 -> NACE rev.2 22"),
    # --- non-metallic minerals ------------------------------------------
    (("GLAS", "CRMC"), "230010", "high",
     "NACE rev.2 23.1 glass and 23.2/23.4 ceramics, DST 'glass and ceramic "
     "products'"),
    (("GLAW",), "230010", "medium",
     "no developer-table entry; assigned by analogy with GLAS, the industry "
     "whose material it re-supplies"),
    (("BRIK", "CMNT", "ONMM"), "230020", "high",
     "NACE rev.2 23.3 clay building materials, 23.5 cement, lime and plaster "
     "and 23.6-23.9, DST 'Manufacture of concrete and bricks'"),
    (("ASHW",), "230020", "medium",
     "no developer-table entry; assigned by analogy with CMNT, since clinker "
     "is NACE rev.2 23.5"),
    # --- metals ----------------------------------------------------------
    (("STEL", "PREM", "ALUM", "LZTP", "COPP", "ONFM", "METC"), "240000",
     "high", "ISIC rev.3 27 -> NACE rev.2 24, developer table 24"),
    (("STEW", "PREW", "ALUW", "LZTW", "COPW", "ONFW"), "240000", "medium",
     "EXIOBASE hybrid secondary-metal activities, developer table 24"),
    (("FABM",), "250000", "high",
     "ISIC rev.3 28 -> NACE rev.2 25; the developer table also lists 33, the "
     "repair and installation division NACE rev.2 created, which no EXIOBASE "
     "industry can supply on its own"),
    # --- machinery, electronics, vehicles, furniture ---------------------
    (("MACH",), "280010;280020", "high",
     "ISIC rev.3 29 -> NACE rev.2 28, which DST splits into engines, "
     "windmills and pumps and other machinery; agrees with the seed group"),
    (("OFMA",), "260010", "high",
     "ISIC rev.3 30 -> NACE rev.2 26.2 computers, DST 'computers and "
     "communication equipment etc.'"),
    (("ELMA",), "270010;270020;270030", "high",
     "ISIC rev.3 31 -> NACE rev.2 27, which DST splits three ways; agrees "
     "with the seed group"),
    (("RATV",), "260010;260020", "high",
     "ISIC rev.3 32 -> NACE rev.2 26.1 components, 26.3 communication "
     "equipment and 26.4 consumer electronics, straddling the DST split"),
    (("MEIN",), "260020;320010", "high",
     "ISIC rev.3 33 -> NACE rev.2 26.5-26.7 instruments = DST 260020 and "
     "32.5 medical and dental instruments = DST 320010; the seed group names "
     "26 only"),
    (("MOTO",), "290000", "high", "ISIC rev.3 34 -> NACE rev.2 29"),
    (("OTRE",), "300000", "high",
     "ISIC rev.3 35 -> NACE rev.2 30, DST 'ships and other transport "
     "equipment'"),
    (("FURN",), "310000;320020", "high",
     "ISIC rev.3 36 -> NACE rev.2 31 furniture and 32.1-32.9 other "
     "manufacturing, which DST separates"),
    # --- recycling, energy, water, waste --------------------------------
    (("RYMS", "BOTW"), "383900", "high",
     "ISIC rev.3 37 -> NACE rev.2 38.3, developer table 38; DST 383900 spans "
     "NACE 38 and 39"),
    (_POW, "350010", "high",
     "NACE rev.2 35.1, DST 'Production and distribution of electricity'; "
     "EXIOBASE's fourteen generation, transmission and distribution "
     "activities have no DST counterpart individually"),
    (("GASD",), "350020", "high",
     "NACE rev.2 35.2, DST 'Manufacture and distribution of gas'"),
    (("HWAT",), "350030", "high",
     "NACE rev.2 35.3, DST 'Steam and hot water supply'"),
    (("WATR",), "360000", "high", "ISIC rev.3 41 -> NACE rev.2 36"),
    (("WASF", "WASO"), "370000", "high",
     "developer table 37, NACE rev.2 37 sewerage, DST 'Sewerage'"),
    (_WASTE_TREATMENT, "383900", "high",
     "developer table 38 39, NACE rev.2 38.2 waste treatment and disposal; "
     "EXIOBASE's eighteen fraction-specific treatment activities all land in "
     "the single DST industry 383900"),
    # --- construction ----------------------------------------------------
    (("CONS",), "410009;420000;430003;430004", "high",
     "ISIC rev.3 45 -> NACE rev.2 41, 42 and 43; agrees with the seed group"),
    (("CONW",), "410009;420000;430003;430004", "medium",
     "developer table 41 42 43 for this hybrid construction-aggregate "
     "activity, although NACE rev.2 would place materials recovery in 38.32"),
    # --- trade, accommodation, transport --------------------------------
    (("TDMO",), "450010;450020", "high",
     "ISIC rev.3 50.1-50.4 -> NACE rev.2 45, which DST splits into sale and "
     "repair of motor vehicles"),
    (("TDFU",), "470000", "high",
     "no developer-table entry; NACE rev.1.1 50.5 retail sale of automotive "
     "fuel moved to NACE rev.2 47.30"),
    (("TDWH",), "460000", "high", "ISIC rev.3 51 -> NACE rev.2 46"),
    (("TDRT",), "470000;950000", "high",
     "ISIC rev.3 52 -> NACE rev.2 47 retail trade and 95.2 repair of "
     "personal and household goods, developer table 47 95"),
    (("HORE",), "550000;560000", "high",
     "ISIC rev.3 55 -> NACE rev.2 55 accommodation and 56 food service"),
    (("TRAI",), "490010;490020", "medium",
     "ISIC rev.3 60.1 rail -> NACE rev.2 49.1/49.2 = DST 490010 and the "
     "suburban-rail part of 49.31 = DST 490020, so a weight is needed"),
    (("TLND",), "490020;490030", "high",
     "ISIC rev.3 60.2 other land transport -> NACE rev.2 49.3 passenger and "
     "49.4 road freight"),
    (("TPIP",), "490030", "high",
     "ISIC rev.3 60.3 -> NACE rev.2 49.5, and DST 490030 is named 'Freight "
     "transport by road and via pipeline'"),
    (("TWAS", "TWAI"), "500000", "high",
     "ISIC rev.3 61.1 and 61.2 -> NACE rev.2 50; DST has one water-transport "
     "industry; agrees with the seed group"),
    (("TAIR",), "510000", "high", "ISIC rev.3 62 -> NACE rev.2 51"),
    (("TAUX",), "520000;790000", "high",
     "ISIC rev.3 63 -> NACE rev.2 52 support activities for transportation "
     "and 79 travel agencies, developer table 52 79"),
    (("PTEL",), "530000;610000", "high",
     "ISIC rev.3 64 -> NACE rev.2 53 postal and courier and 61 "
     "telecommunications, developer table 53 61; the seed group names 61 "
     "only"),
    # --- finance, real estate, business services ------------------------
    (("FINT",), "640010;640020", "high",
     "ISIC rev.3 65 -> NACE rev.2 64, which DST splits into monetary "
     "intermediation and mortgage credit"),
    (("FINS",), "650000", "high", "ISIC rev.3 66 -> NACE rev.2 65"),
    (("FAUX",), "660000", "high", "ISIC rev.3 67 -> NACE rev.2 66"),
    (("REAL",), "680010;680030;680023;680024", "high",
     "ISIC rev.3 70 -> NACE rev.2 68, which DST splits four ways including "
     "owner-occupied dwellings"),
    (("MARE",), "770000", "high", "ISIC rev.3 71 -> NACE rev.2 77"),
    (("COMP",), "580020;620000;630000", "high",
     "ISIC rev.3 72 -> NACE rev.2 62 IT services, 63.1 information services "
     "and 58.2 software publishing, developer table 58 62 63"),
    (("RESD",), "720001;720002", "high",
     "ISIC rev.3 73 -> NACE rev.2 72, which DST splits into market and "
     "non-market research"),
    (("OBUS",),
     "690010;690020;700000;710000;730000;740000;780000;800000;810000;820000",
     "high",
     "ISIC rev.3 74 is the largest split in NACE rev.2: divisions 69 legal "
     "and accounting, 70 management consultancy, 71 architecture and "
     "engineering, 73 advertising, 74 other professional, 78 employment, 80 "
     "security, 81 building services and 82 business support, all listed in "
     "the developer table"),
    # --- public administration, education, health -----------------------
    (("PADF",), "840010;840022;840021", "high",
     "ISIC rev.3 75 -> NACE rev.2 84; agrees with the seed group"),
    (("EDUC",), "850010;850020;850030;850042;850041", "high",
     "ISIC rev.3 80 -> NACE rev.2 85, which DST splits five ways; agrees "
     "with the seed group"),
    (("HEAL",), "750000;860010;860020;870000;880000", "high",
     "ISIC rev.3 85 covers human health 85.1, veterinary 85.2 and social "
     "work 85.3, which NACE rev.2 splits into 86, 75 and 87/88; developer "
     "table 75 86 87 88; the seed group names 86, 87 and 88 only"),
    # --- other services ---------------------------------------------------
    (("ORGA",), "940000", "high", "ISIC rev.3 91 -> NACE rev.2 94"),
    (("RECR",),
     "590000;600000;900000;910001;910002;920000;930011;930012;930020", "high",
     "ISIC rev.3 92 -> NACE rev.2 59.1 motion picture, 60 broadcasting, 90 "
     "creative arts, 91 libraries and museums, 92 gambling and 93 sports and "
     "recreation, all listed in the developer table"),
    (("OSER",), "960000", "high",
     "ISIC rev.3 93 -> NACE rev.2 96 other personal service activities"),
    (("PRHH",), "970000", "high",
     "ISIC rev.3 95 -> NACE rev.2 97; NACE rev.2 98, undifferentiated "
     "household production, has no DST 117 industry"),
    (("EXTO",), "", "high",
     "NACE rev.2 99 extra-territorial organisations and bodies lies outside "
     "the Danish production boundary and has no DST 117 industry"),
]


# ---------------------------------------------------------------------------
# loaders
# ---------------------------------------------------------------------------
def load_exiobase_industries() -> pd.DataFrame:
    """Read the ordered EXIOBASE 163-industry list.

    Returns
    -------
    pandas.DataFrame
        Columns ``exiobase_position`` (0-based, the position in the ``x``
        vector), ``exiobase_code`` (the four-letter code without the ``A_``
        prefix), ``exiobase_name`` and ``exiobase_code1`` (the ``i``-prefixed
        ISIC rev.3 based code). 163 rows, ordered by position.
    """
    frame = pd.read_excel(CLASSIFICATIONS, sheet_name="disagg_ind", skiprows=5)
    frame = frame[frame["Position"].notna()].copy()
    frame["exiobase_position"] = frame["Position"].astype(int)
    frame["exiobase_code"] = frame["Code"].str.replace("^A_", "", regex=True)
    frame["exiobase_name"] = frame["Description"].str.strip()
    frame["exiobase_code1"] = frame["Code1"].astype(str)
    out = frame[["exiobase_position", "exiobase_code", "exiobase_name",
                 "exiobase_code1"]].reset_index(drop=True)
    if len(out) != N_SECTORS:
        raise ValueError(f"expected {N_SECTORS} industries, read {len(out)}")
    return out


def isic_division(code1: str) -> str:
    """Two-digit ISIC rev.3 division carried by an EXIOBASE ``Code1``.

    Parameters
    ----------
    code1 : str
        An EXIOBASE industry code of the ``i<division>[.<detail>]`` form, for
        example ``i01.a``, ``i13.20.11`` or ``i90.5.f``.

    Returns
    -------
    str
        The division, zero padded to two digits.
    """
    match = re.match(r"i(\d+)", code1)
    if match is None:
        raise ValueError(f"cannot read an ISIC division from {code1!r}")
    return match.group(1).zfill(2)


def load_isic_reference() -> dict[str, str]:
    """ISIC rev.3 divisions from the existing bronze concordance, for checking.

    Returns
    -------
    dict of str to str
        EXIOBASE industry code to two-digit ISIC rev.3 division. Covers 138 of
        the 163 industries; the file predates the hybrid activities.
    """
    frame = pd.read_csv(ISIC_CSV, dtype={"isic_rev3_division": str})
    return dict(zip(frame["exiobase_industry_code"],
                    frame["isic_rev3_division"].str.zfill(2)))


def load_dst_industries(year: str) -> pd.DataFrame:
    """Read the DST 117-industry codes, names and total output.

    Parameters
    ----------
    year : str
        Reference year of the published Danish input-output table.

    Returns
    -------
    pandas.DataFrame
        Columns ``dst_industry_code``, ``dst_industry_name`` and
        ``dst_output_meur``, in workbook order. The output row is the table's
        ``Total Output`` row, converted from 1000 DKK to M.EUR at the annual
        average rate, exactly as ``vintage_defect_audit._dst_output`` does.
    """
    sheet = pd.read_excel(str(DST_IO).format(year=year), sheet_name="IO",
                          header=None)
    codes = [str(v).strip() for v in sheet.iloc[2, 2:].tolist()]
    names = [str(v).strip() for v in sheet.iloc[1, 2:].tolist()]
    labels = [str(v) for v in sheet.iloc[:, 0].tolist()]
    row = max(i for i, v in enumerate(labels)
              if v.strip().lower() == "total output")
    values = pd.to_numeric(sheet.iloc[row, 2:], errors="coerce").values
    rate = DKK_PER_EUR[str(year)]
    rows = [dict(dst_industry_code=code, dst_industry_name=name,
                 dst_output_meur=float(value) / 1e3 / rate)
            for code, name, value in zip(codes, names, values)
            if re.fullmatch(r"\d{6}", code) and np.isfinite(value)]
    frame = pd.DataFrame(rows)
    if len(frame) != 117:
        raise ValueError(f"expected 117 DST industries, read {len(frame)}")
    return frame


def load_dst_totals(year: str) -> pd.DataFrame:
    """Danish output and total imports by DST industry, in bn DKK.

    The published table is read a second time rather than derived from
    :func:`load_dst_industries` because the split weights must not depend on
    the euro conversion: a share within a group is scale-free, and reporting
    intensities per bn DKK keeps this function free of an exchange rate.

    Parameters
    ----------
    year : str
        Reference year of the published Danish input-output table.

    Returns
    -------
    pandas.DataFrame
        Columns ``dst_industry_code``, ``dst_output_bndkk`` and
        ``dst_imports_bndkk``. Output is the ``Total Output`` row of the
        industry columns; imports are the ``Total`` column of the ``Imports``
        row block, so they cover intermediate use, final consumption, capital
        formation and re-exports alike, which is the vector a SNAC import
        estimate multiplies.

    Raises
    ------
    ValueError
        If the workbook does not yield 117 industries and 117 import rows.
    """
    sheet = pd.read_excel(str(DST_IO).format(year=year), sheet_name="IO",
                          header=None)
    labels = [str(v).strip() for v in sheet.iloc[:, 0].tolist()]
    header = [str(v).strip() for v in sheet.iloc[2, :].tolist()]
    banner = [str(v).strip() for v in sheet.iloc[0, :].tolist()]

    industry_columns = {code: j for j, code in enumerate(header)
                        if re.fullmatch(r"\d{6}", code)}
    output_row = max(i for i, v in enumerate(labels)
                     if v.lower() == "total output")
    imports_row = labels.index("Imports")
    total_column = banner.index("Total")

    # the DST product codes of the Imports block, which repeats the 117 codes
    import_rows = {label: i for i, label in enumerate(labels)
                   if i > imports_row and re.fullmatch(r"\d{6}", label)}

    output = {code: float(sheet.iat[output_row, j]) / 1e6
              for code, j in industry_columns.items()}
    imports = {code: float(sheet.iat[i, total_column]) / 1e6
               for code, i in import_rows.items()}
    if len(output) != 117 or len(imports) != 117:
        raise ValueError(f"read {len(output)} output and {len(imports)} "
                         f"import rows from the {year} table, expected 117")
    return pd.DataFrame([
        dict(dst_industry_code=code, dst_output_bndkk=output[code],
             dst_imports_bndkk=imports[code])
        for code in output])


def load_dst_direct_ghg(year: str) -> dict[str, float]:
    """Danish direct greenhouse gas emissions by DST industry, kt CO2e.

    Parameters
    ----------
    year : str
        Reference year present in the satellite extract.

    Returns
    -------
    dict of str to float
        DST industry code without the ``V`` prefix, to ``GHGEXBIO``: the
        territorial account excluding biogenic carbon dioxide, on the direct
        allocation principle, which is the Scope 1 concept a domestic
        technology assumption needs.

    Raises
    ------
    ValueError
        If the extract does not carry 117 industries for the year.
    """
    frame = pd.read_csv(SATELLITE_CSV, comment="#")
    part = frame[(frame.year == int(year))
                 & (frame.account == "greenhouse_gas")
                 & (frame.substance == "GHGEXBIO")]
    values = {str(code)[1:]: float(value)
              for code, value in zip(part.industry_code, part.value)}
    if len(values) != 117:
        raise ValueError(f"{year} carries {len(values)} industries in "
                         f"{SATELLITE_CSV.name}, expected 117")
    return values


def load_exiobase_dk_output(year: str) -> np.ndarray:
    """Danish total output by EXIOBASE industry, M.EUR.

    Parameters
    ----------
    year : str
        EXIOBASE reference year; the directory is resolved under
        ``paths.EXIOBASE_DIR``, which points at the background vintage this
        study uses (v3.8.2).

    Returns
    -------
    numpy.ndarray
        163 total outputs, read from the distribution's ``x.txt`` in the same
        way as ``vintage_defect_audit._exiobase_x``.
    """
    path = str(EXIOBASE_X).format(year=year)
    frame = pd.read_csv(path, sep="\t", index_col=[0, 1])
    vector = np.asarray(frame).ravel()
    dk = vector[K_DK * N_SECTORS:(K_DK + 1) * N_SECTORS]
    if dk.size != N_SECTORS:
        raise ValueError(f"unexpected x length {vector.size} in {path}")
    return dk


# ---------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------
def _split(codes: str) -> list[str]:
    return [c for c in codes.split(";") if c]


def _shares(targets: list[str], size: dict[str, float]) -> str:
    """Semicolon-joined shares of a row's DST industries, summing to one.

    These are the non-zero entries of the ``K`` bridge in ``e_m = Q K m``. A
    one-to-many row has to divide one EXIOBASE industry's import value between
    several Danish industries, and the divisor decides which Danish intensity
    the import inherits; a row with a single target trivially gets ``1.0``, and
    an unmatched row gets the empty string.

    Parameters
    ----------
    targets : list of str
        The row's DST industry codes, in the order they are written out.
    size : dict of str to float
        The weighting variable by DST industry code, output or imports.

    Returns
    -------
    str
        Shares to six decimals, in ``targets`` order, joined by semicolons.
        Where the variable sums to zero over the row the shares fall back to
        equal weights, so a share vector is always defined and always sums to
        one.
    """
    if not targets:
        return ""
    values = np.array([size.get(code, 0.0) for code in targets], dtype=float)
    total = values.sum()
    if total <= 0:
        values = np.ones(len(targets))
        total = float(len(targets))
    return ";".join(f"{v / total:.6f}" for v in values)


def _components(pairs: Iterable[tuple[str, str]]) -> dict[str, int]:
    """Connected components of the bipartite EXIOBASE-DST mapping graph.

    Parameters
    ----------
    pairs : iterable of (str, str)
        ``(exiobase node, dst node)`` edges, each node already namespaced.

    Returns
    -------
    dict of str to int
        Node to component index. Components make the output comparison
        apples-to-apples: within a component, every EXIOBASE industry that
        supplies any of the DST industries is present, and vice versa, so the
        two totals cover the same economic ground.
    """
    parent: dict[str, str] = {}

    def find(node: str) -> str:
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for left, right in pairs:
        union(left, right)
    roots = {}
    for node in list(parent):
        roots.setdefault(find(node), len(roots))
    return {node: roots[find(node)] for node in parent}


def build_concordance(year: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Assemble the EXIOBASE-to-DST concordance from ``MAPPING``.

    Parameters
    ----------
    year : str
        Reference year, used to read the DST industry names.

    Returns
    -------
    concordance : pandas.DataFrame
        One row per EXIOBASE industry, ordered by EXIOBASE position.
    dst : pandas.DataFrame
        The DST 117-industry frame, returned so callers do not re-read it.

    Raises
    ------
    ValueError
        If ``MAPPING`` does not cover each of the 163 industries exactly once,
        or names a DST industry that is not in the published table.
    """
    industries = load_exiobase_industries()
    dst = load_dst_industries(year)
    dst_name = dict(zip(dst["dst_industry_code"], dst["dst_industry_name"]))
    isic_reference = load_isic_reference()
    totals = load_dst_totals(year).set_index("dst_industry_code")
    output = totals["dst_output_bndkk"].to_dict()
    imports = totals["dst_imports_bndkk"].to_dict()

    assigned: dict[str, tuple[str, str, str]] = {}
    for codes, targets, confidence, basis in MAPPING:
        for code in codes:
            if code in assigned:
                raise ValueError(f"{code} appears twice in MAPPING")
            for target in _split(targets):
                if target not in dst_name:
                    raise ValueError(f"{code} names unknown DST {target}")
            assigned[code] = (targets, confidence, basis)
    missing = set(industries["exiobase_code"]) - set(assigned)
    extra = set(assigned) - set(industries["exiobase_code"])
    if missing or extra:
        raise ValueError(f"MAPPING gaps {sorted(missing)}, "
                         f"unknown codes {sorted(extra)}")

    # how many EXIOBASE industries each DST industry receives, for the row type
    received: dict[str, int] = {}
    for code in industries["exiobase_code"]:
        for target in _split(assigned[code][0]):
            received[target] = received.get(target, 0) + 1

    edges = [(f"E:{code}", f"D:{target}")
             for code in industries["exiobase_code"]
             for target in _split(assigned[code][0])]
    component = _components(edges)

    rows = []
    for _, industry in industries.iterrows():
        code = industry["exiobase_code"]
        targets, confidence, basis = assigned[code]
        target_list = _split(targets)
        prefixes = sorted({t[:2] for t in target_list})
        if not target_list:
            mapping_type = "unmatched"
        elif len(target_list) > 1:
            mapping_type = "one-to-many"
        elif received[target_list[0]] > 1:
            mapping_type = "many-to-one"
        else:
            mapping_type = "one-to-one"
        division = isic_division(industry["exiobase_code1"])
        reference = isic_reference.get(code, "")
        rows.append(dict(
            exiobase_position=int(industry["exiobase_position"]),
            exiobase_code=code,
            exiobase_name=industry["exiobase_name"],
            exiobase_code1=industry["exiobase_code1"],
            isic_rev3_division=division,
            isic_rev3_division_bronze_csv=reference,
            nace_rev2_candidates_developer=DEVELOPER_NACE2.get(code, ""),
            dst_nace_prefix=";".join(prefixes),
            dst_industry_code=";".join(target_list),
            dst_industry_name=";".join(dst_name[t] for t in target_list),
            mapping_type=mapping_type,
            confidence=confidence,
            basis=basis,
            mapping_group=(component[f"E:{code}"] if target_list else -1),
            dst_output_share=_shares(target_list, output),
            dst_import_share=_shares(target_list, imports),
        ))
    concordance = pd.DataFrame(rows)

    # group-level type, and a stable human-readable group label
    labels, types = {}, {}
    for group, part in concordance[concordance.mapping_group >= 0].groupby(
            "mapping_group"):
        exio = len(part)
        targets = sorted({t for row in part["dst_industry_code"]
                          for t in _split(row)})
        divisions = ";".join(sorted({t[:2] for t in targets}))
        principal = part[part.confidence == "high"]
        lead = (principal if len(principal) else part)["exiobase_code"].iat[0]
        labels[group] = f"NACE {divisions} ({lead})"
        if exio == 1 and len(targets) == 1:
            types[group] = "one-to-one"
        elif exio == 1:
            types[group] = "one-to-many"
        elif len(targets) == 1:
            types[group] = "many-to-one"
        else:
            types[group] = "many-to-many"
    concordance["mapping_group_label"] = [
        labels.get(g, "unmatched") for g in concordance["mapping_group"]]
    concordance["mapping_group_type"] = [
        types.get(g, "unmatched") for g in concordance["mapping_group"]]
    return concordance, dst


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------
def _row(check: str, subject: str, **kwargs) -> dict[str, object]:
    row: dict[str, object] = dict(
        check=check, subject=subject, exiobase_industries="",
        dst_industries="", exiobase_output_meur=np.nan,
        dst_output_meur=np.nan, output_difference_meur=np.nan,
        ratio_exiobase_over_dst=np.nan,
        ratio_relative_to_national_aggregate=np.nan,
        share_of_exiobase_output_pct=np.nan, share_of_dst_output_pct=np.nan,
        flag="", detail="")
    row.update(kwargs)
    return row


def validate(concordance: pd.DataFrame, dst: pd.DataFrame,
             dk_output: np.ndarray, year: str) -> pd.DataFrame:
    """Test the concordance and return the validation report.

    Four things are tested. Completeness and agreement with
    ``vintage_defect_audit.CONCORDANCE`` are assertions, because a failure
    means the concordance is wrong. The output comparison and the confidence
    coverage are measurements, because a failure there can mean either a
    mapping error or a difference between the two databases.

    Parameters
    ----------
    concordance : pandas.DataFrame
        Output of :func:`build_concordance`.
    dst : pandas.DataFrame
        DST 117-industry frame with total output in M.EUR.
    dk_output : numpy.ndarray
        EXIOBASE Danish total output by industry, M.EUR.
    year : str
        Reference year, recorded in the report.

    Returns
    -------
    pandas.DataFrame
        Long-format report: one row per check per subject.

    Raises
    ------
    AssertionError
        If an industry is missing or duplicated, or if a seed group's NACE
        prefixes do not all survive in the concordance.
    """
    dst_output = dict(zip(dst["dst_industry_code"], dst["dst_output_meur"]))
    dst_name = dict(zip(dst["dst_industry_code"], dst["dst_industry_name"]))
    position = dict(zip(concordance["exiobase_code"],
                        concordance["exiobase_position"]))
    exio_total = float(dk_output.sum())
    dst_total = float(sum(dst_output.values()))
    national = exio_total / dst_total
    rows: list[dict[str, object]] = []

    # 1 completeness -------------------------------------------------------
    counts = concordance["exiobase_position"].value_counts()
    duplicated = sorted(counts[counts > 1].index)
    absent = sorted(set(range(N_SECTORS)) - set(concordance.exiobase_position))
    complete = len(concordance) == N_SECTORS and not duplicated and not absent
    rows.append(_row(
        "completeness", "every EXIOBASE industry appears exactly once",
        exiobase_industries=str(len(concordance)),
        flag="pass" if complete else "FAIL",
        detail=f"{len(concordance)} rows, {N_SECTORS} expected; "
               f"duplicated {duplicated}; absent {absent}"))
    assert complete, f"duplicated {duplicated}, absent {absent}"

    # 2 agreement with the seed concordance --------------------------------
    for label, indices, prefixes in SEED_CONCORDANCE:
        codes = concordance.loc[
            concordance.exiobase_position.isin(indices), "exiobase_code"]
        mine = sorted({p for code in codes
                       for p in concordance.loc[
                           concordance.exiobase_code == code,
                           "dst_nace_prefix"].iat[0].split(";") if p})
        held = set(prefixes) <= set(mine)
        status = "exact" if set(mine) == set(prefixes) else "refined"
        seed_dst = sum(v for c, v in dst_output.items()
                       if any(c.startswith(p) for p in prefixes))
        seed_exio = float(dk_output[list(indices)].sum())
        rows.append(_row(
            "seed_agreement", label,
            exiobase_industries=";".join(str(i) for i in indices),
            dst_industries=";".join(prefixes),
            exiobase_output_meur=round(seed_exio, 1),
            dst_output_meur=round(seed_dst, 1),
            ratio_exiobase_over_dst=round(seed_exio / seed_dst, 3),
            ratio_relative_to_national_aggregate=round(
                seed_exio / seed_dst / national, 3),
            flag=("pass" if held else "FAIL")
                 + ("" if 1.0 / FLAG_FACTOR <= seed_exio / seed_dst
                    <= FLAG_FACTOR else "; ratio off by more than 2x"),
            detail=f"seed prefixes {';'.join(prefixes)} {status} in this "
                   f"concordance, which assigns {';'.join(mine)}; the two "
                   f"outputs above are the seed's own groups, on EXIOBASE "
                   f"{year}"))
        assert held, f"{label}: seed {prefixes} not contained in {mine}"

    # 3 output comparison, per concordance group ---------------------------
    matched = concordance[concordance.mapping_group >= 0]
    is_hybrid = dict(zip(concordance["exiobase_code"],
                         concordance["exiobase_code1"].str.contains(r"\.w")))
    for group, part in matched.groupby("mapping_group"):
        codes = list(part["exiobase_code"])
        targets = sorted({t for row in part["dst_industry_code"]
                          for t in _split(row)})
        exio = float(dk_output[[position[c] for c in codes]].sum())
        national_accounts = sum(dst_output[t] for t in targets)
        ratio = exio / national_accounts if national_accounts else np.nan
        flag = ""
        if not np.isfinite(ratio) or ratio > FLAG_FACTOR \
                or ratio < 1.0 / FLAG_FACTOR:
            flag = "OFF BY MORE THAN 2x"
        confidences = sorted(set(part["confidence"]))
        hybrid = float(dk_output[[position[c] for c in codes
                                  if is_hybrid[c]]].sum()) if codes else 0.0
        rows.append(_row(
            "group_output", part["mapping_group_label"].iat[0],
            exiobase_industries=";".join(codes),
            dst_industries=";".join(targets),
            exiobase_output_meur=round(exio, 1),
            dst_output_meur=round(national_accounts, 1),
            output_difference_meur=round(exio - national_accounts, 1),
            ratio_exiobase_over_dst=round(ratio, 3),
            ratio_relative_to_national_aggregate=round(ratio / national, 3),
            flag=flag,
            detail=f"{part['mapping_group_type'].iat[0]}, "
                   f"{len(codes)} EXIOBASE into {len(targets)} DST, "
                   f"confidence {'/'.join(confidences)}; "
                   f"{100 * hybrid / exio if exio else 0:.0f} % of the "
                   f"EXIOBASE side is hybrid re-processing activity that has "
                   f"no DST industry"))

    # 4 confidence coverage -------------------------------------------------
    for confidence in ("high", "medium", "low", "unmatched"):
        if confidence == "unmatched":
            part = concordance[concordance.mapping_type == "unmatched"]
        else:
            part = concordance[(concordance.confidence == confidence)
                               & (concordance.mapping_type != "unmatched")]
        exio = float(dk_output[[position[c]
                               for c in part["exiobase_code"]]].sum()) \
            if len(part) else 0.0
        targets = sorted({t for row in part["dst_industry_code"]
                          for t in _split(row)})
        national_accounts = sum(dst_output[t] for t in targets)
        rows.append(_row(
            "confidence_coverage", confidence,
            exiobase_industries=str(len(part)),
            dst_industries=str(len(targets)),
            exiobase_output_meur=round(exio, 1),
            dst_output_meur=round(national_accounts, 1),
            share_of_exiobase_output_pct=round(100 * exio / exio_total, 2),
            share_of_dst_output_pct=round(
                100 * national_accounts / dst_total, 2),
            detail=f"{100 * exio / exio_total:.1f} % of EXIOBASE Danish "
                   f"output, {100 * national_accounts / dst_total:.1f} % of "
                   f"DST output (DST shares overlap where one DST industry "
                   f"receives industries of different confidence)"))

    # 5 DST-side gaps -------------------------------------------------------
    sourced = {t for row in matched["dst_industry_code"] for t in _split(row)}
    gaps = [c for c in dst["dst_industry_code"] if c not in sourced]
    for code in gaps:
        rows.append(_row(
            "dst_side_gap", f"{code} {dst_name[code]}",
            dst_industries=code, dst_output_meur=round(dst_output[code], 1),
            flag="NO EXIOBASE SOURCE",
            detail="no EXIOBASE industry corresponds; imports recorded "
                   "against this DST industry cannot be given an EXIOBASE "
                   "intensity without a rule invented outside this "
                   "concordance"))
    rows.append(_row(
        "dst_side_gap", "total DST output with no EXIOBASE source",
        dst_industries=str(len(gaps)),
        dst_output_meur=round(sum(dst_output[c] for c in gaps), 1),
        detail=f"{100 * sum(dst_output[c] for c in gaps) / dst_total:.2f} % "
               f"of Danish output; {117 - len(gaps)} of 117 DST industries "
               f"are sourced"))

    # 6 the EXIOBASE hybrid activities, which have no DST industry at all ---
    hybrid = concordance[concordance.exiobase_code1.str.contains(r"\.w")]
    hybrid_output = float(dk_output[[position[c]
                                    for c in hybrid["exiobase_code"]]].sum())
    rows.append(_row(
        "hybrid_activity_effect",
        "EXIOBASE secondary-material re-processing activities",
        exiobase_industries=";".join(hybrid["exiobase_code"]),
        exiobase_output_meur=round(hybrid_output, 1),
        detail=f"{len(hybrid)} activities carrying "
               f"{100 * hybrid_output / exio_total:.1f} % of EXIOBASE Danish "
               f"output; the national accounts have no separate industry for "
               f"any of them, so they inflate the EXIOBASE side of whichever "
               f"group they sit in. Each group row reports its own hybrid "
               f"share: it accounts for the whole of the NACE 16 flag (the "
               f"wood group falls to 1.05 without WOOW in 2022) but only part "
               f"of the NACE 23 and NACE 24 flags"))

    # 7 where the level gap actually lives -----------------------------------
    ranked = [r for r in rows if r["check"] == "group_output"]
    ranked.sort(key=lambda r: -abs(float(r["output_difference_meur"])))
    for rank, entry in enumerate(ranked[:6], start=1):
        rows.append(_row(
            "gap_decomposition", f"{rank}. {entry['subject']}",
            exiobase_industries=entry["exiobase_industries"],
            dst_industries=entry["dst_industries"],
            exiobase_output_meur=entry["exiobase_output_meur"],
            dst_output_meur=entry["dst_output_meur"],
            output_difference_meur=entry["output_difference_meur"],
            ratio_exiobase_over_dst=entry["ratio_exiobase_over_dst"],
            detail=f"{100 * abs(float(entry['output_difference_meur']))
                        / abs(exio_total - dst_total):.1f} % of the absolute "
                   f"gap between the two Danish totals"))

    # 8 division rollup: the coarsest partition the mapping is certain at ---
    division_edges = []
    for group, part in matched.groupby("mapping_group"):
        for division in sorted({t[:2] for row in part["dst_industry_code"]
                                for t in _split(row)}):
            division_edges.append((f"G:{group}", f"N:{division}"))
    rollup = _components(division_edges)
    buckets: dict[int, list[int]] = {}
    for group in matched["mapping_group"].unique():
        buckets.setdefault(rollup[f"G:{group}"], []).append(int(group))
    for _, groups in sorted(buckets.items()):
        part = matched[matched.mapping_group.isin(groups)]
        codes = list(part["exiobase_code"])
        targets = sorted({t for row in part["dst_industry_code"]
                          for t in _split(row)})
        exio = float(dk_output[[position[c] for c in codes]].sum())
        national_accounts = sum(dst_output[t] for t in targets)
        ratio = exio / national_accounts if national_accounts else np.nan
        divisions = ";".join(sorted({t[:2] for t in targets}))
        flag = ""
        if not np.isfinite(ratio) or ratio > FLAG_FACTOR \
                or ratio < 1.0 / FLAG_FACTOR:
            flag = "OFF BY MORE THAN 2x"
        rows.append(_row(
            "division_rollup", f"NACE {divisions}",
            exiobase_industries=str(len(codes)),
            dst_industries=";".join(targets),
            exiobase_output_meur=round(exio, 1),
            dst_output_meur=round(national_accounts, 1),
            output_difference_meur=round(exio - national_accounts, 1),
            ratio_exiobase_over_dst=round(ratio, 3),
            ratio_relative_to_national_aggregate=round(ratio / national, 3),
            flag=flag,
            detail=f"{len(groups)} concordance group(s) merged to the NACE "
                   f"division, the coarsest level at which the correspondence "
                   f"is certain; a flag that clears here was a "
                   f"within-division allocation difference, not a mapping "
                   f"error"))

    # 9 aggregate -----------------------------------------------------------
    rows.append(_row(
        "aggregate", "all industries",
        exiobase_industries=str(N_SECTORS), dst_industries="117",
        exiobase_output_meur=round(exio_total, 1),
        dst_output_meur=round(dst_total, 1),
        ratio_exiobase_over_dst=round(national, 3),
        ratio_relative_to_national_aggregate=1.0,
        detail=f"EXIOBASE Danish total output against Statistics Denmark "
               f"{year}; every group ratio is read against this number, not "
               f"against 1"))

    report = pd.DataFrame(rows)
    report.insert(0, "reference_year", year)
    report.insert(1, "source_national_accounts",
                  f"Statistics Denmark, published 117-industry input-output "
                  f"table {year}, 'Total Output' row")
    report.insert(2, "source_concordance", DEVELOPER_SOURCE)
    return report


def split_sensitivity(concordance: pd.DataFrame,
                      years: Iterable[str] = WEIGHT_YEARS) -> pd.DataFrame:
    """How much the choice of split weight moves a one-to-many row's intensity.

    A one-to-many row divides one EXIOBASE industry between several Danish
    industries whose emission intensities can differ by more than an order of
    magnitude, so the divisor is a substantive modelling choice rather than
    bookkeeping. Three admissible readings are compared:

    ``import``
        Shares of Danish total imports of the row's products. This is the
        vector a simplified-SNAC estimate actually multiplies, so it is the
        sharpest reading of ``K`` for an import-side bridge and the one this
        module recommends.
    ``output``
        Shares of Danish output, the production-share proxy of Palm et al.
        (2019). Reported because it is the published convention.
    ``equal``
        One over the number of targets: what a bridge carrying no weights
        implies if its user averages, and the reason a binary incidence matrix
        is not a neutral default.

    Parameters
    ----------
    concordance : pandas.DataFrame
        The frame returned by :func:`build_concordance`.
    years : iterable of str, optional
        Reference years to report. Each must be covered by both the published
        input-output table and the DST satellite.

    Returns
    -------
    pandas.DataFrame
        One row per one-to-many EXIOBASE industry per year. Intensities are
        kt CO2e per bn DKK of output, which is also kg CO2e per 1000 DKK, so
        no exchange rate enters. ``ratio_import_over_output`` and
        ``ratio_equal_over_import`` are the decision-relevant columns:
        a value far from one means the row's Danish intensity depends on the
        weighting choice and the choice has to be stated.
        ``group_imports_bndkk`` is the guard on the import weighting: care and
        social services are barely traded, so a row whose group imports little
        rests its import shares on a small base and should be weighted on
        output instead.
    """
    rows: list[dict[str, object]] = []
    splits = concordance[concordance.mapping_type == "one-to-many"]
    for year in years:
        totals = load_dst_totals(year).set_index("dst_industry_code")
        output = totals["dst_output_bndkk"].to_dict()
        imports = totals["dst_imports_bndkk"].to_dict()
        emissions = load_dst_direct_ghg(year)
        national = (sum(emissions.values())
                    / sum(output[c] for c in output if c in emissions))
        for row in splits.itertuples():
            targets = _split(row.dst_industry_code)
            e = np.array([emissions[c] for c in targets])
            x = np.array([output[c] for c in targets])
            m = np.array([imports[c] for c in targets])
            q = np.divide(e, x, out=np.zeros_like(e), where=x > 0)
            w_out = x / x.sum() if x.sum() > 0 else np.ones(len(x)) / len(x)
            w_imp = m / m.sum() if m.sum() > 0 else w_out
            q_out = float(q @ w_out)
            q_imp = float(q @ w_imp)
            q_eq = float(q.mean())
            positive = q[q > 0]
            rows.append(dict(
                reference_year=year,
                exiobase_code=row.exiobase_code,
                exiobase_name=row.exiobase_name,
                dst_industries=row.dst_industry_code,
                n_dst=len(targets),
                dst_output_share=row.dst_output_share,
                dst_import_share=row.dst_import_share,
                member_intensity_kt_per_bndkk=";".join(f"{v:.3f}" for v in q),
                q_import_weighted=q_imp,
                q_output_weighted=q_out,
                q_equal_weighted=q_eq,
                q_min=float(positive.min()) if positive.size else 0.0,
                q_max=float(q.max()),
                spread_within_group=(float(q.max() / positive.min())
                                     if positive.size else np.inf),
                ratio_import_over_output=(q_imp / q_out if q_out > 0
                                          else np.nan),
                ratio_equal_over_import=(q_eq / q_imp if q_imp > 0
                                         else np.nan),
                q_import_relative_to_national=q_imp / national,
                group_imports_bndkk=float(m.sum()),
                group_output_bndkk=float(x.sum()),
                import_penetration=(float(m.sum() / (m.sum() + x.sum()))
                                    if (m.sum() + x.sum()) > 0 else np.nan),
            ))
    return pd.DataFrame(rows)


def main() -> None:
    """Build the concordance, validate both years, and write both files."""
    year = ANALYSIS_YEAR
    concordance, dst = build_concordance(year)
    CONCORDANCE_CSV.parent.mkdir(parents=True, exist_ok=True)
    concordance.to_csv(CONCORDANCE_CSV, index=False)

    years = list(dict.fromkeys([CONTROL_YEAR, year]))
    reports = []
    for one in years:
        _, dst_year = build_concordance(one)
        reports.append(validate(concordance, dst_year,
                                load_exiobase_dk_output(one), one))
    report = pd.concat(reports, ignore_index=True)
    out_dir = OUTPUT_DIR / FOLDER
    out_dir.mkdir(parents=True, exist_ok=True)
    report.to_csv(out_dir / VALIDATION_CSV, index=False)
    sensitivity = split_sensitivity(concordance)
    sensitivity.to_csv(out_dir / SENSITIVITY_CSV, index=False)

    pd.set_option("display.width", 230)
    pd.set_option("display.max_colwidth", 44)
    show = ["check", "subject", "exiobase_output_meur", "dst_output_meur",
            "ratio_exiobase_over_dst", "ratio_relative_to_national_aggregate",
            "flag"]
    for one in years:
        part = report[report.reference_year == one]
        note = ("  (control: a genuine EXIOBASE reference year)"
                if one == CONTROL_YEAR else "")
        print(f"\n{'=' * 100}\n{one}{note}\n{'=' * 100}")
        print(part[show].to_string(index=False))
        flagged = part[(part.check == "group_output") & (part.flag != "")]
        print(f"groups flagged in {one}: {len(flagged)} of "
              f"{(part.check == 'group_output').sum()}")

    print(f"\nmapping types: "
          f"{concordance.mapping_type.value_counts().to_dict()}")
    print(f"confidence:    {concordance.confidence.value_counts().to_dict()}")
    both = report[(report.check == "group_output") & (report.flag != "")]
    counted = both.groupby("subject")["reference_year"].apply(list)
    persistent = [k for k, v in counted.items() if len(v) == len(years)]
    print(f"\ngroups flagged in EVERY year ({len(persistent)}): {persistent}")
    mismatch = concordance[
        (concordance.isic_rev3_division_bronze_csv != "")
        & (concordance.isic_rev3_division_bronze_csv
           != concordance.isic_rev3_division)]
    if len(mismatch):
        print("\nISIC division disagreements against the bronze CSV:")
        columns = ["exiobase_code", "exiobase_code1", "isic_rev3_division",
                   "isic_rev3_division_bronze_csv"]
        print(mismatch[columns].to_string(index=False))
    latest = sensitivity[sensitivity.reference_year == ANALYSIS_YEAR]
    show_weights = ["exiobase_code", "dst_industries", "q_import_weighted",
                    "q_output_weighted", "q_equal_weighted",
                    "spread_within_group", "ratio_import_over_output"]
    print(f"\n{'=' * 100}\nsplit-weight sensitivity, {ANALYSIS_YEAR}, "
          f"kt CO2e per bn DKK\n{'=' * 100}")
    print(latest.sort_values("q_import_weighted", ascending=False)
          [show_weights].to_string(index=False))
    moved = latest[(latest.ratio_import_over_output > 1.25)
                   | (latest.ratio_import_over_output < 0.8)]
    print(f"\nrows whose intensity moves by more than a quarter between the "
          f"import and output weighting: {len(moved)} of {len(latest)} "
          f"({', '.join(moved.exiobase_code)})")

    print(f"\nwritten -> {CONCORDANCE_CSV}")
    print(f"written -> {out_dir / VALIDATION_CSV}")
    print(f"written -> {out_dir / SENSITIVITY_CSV}")


if __name__ == "__main__":
    main()
