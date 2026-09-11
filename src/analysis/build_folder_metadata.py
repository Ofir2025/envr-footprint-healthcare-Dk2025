# -*- coding: utf-8 -*-
"""Write a metadata readme and data dictionary into every gold table folder.

A reader opening ``data/gold/results/07_malik_replication/`` should not have to
guess what is in it. This module writes a ``readme.md`` per folder describing
what the layer answers, which module produced it, and, for every table, its
grain, row count, columns, units, and dimension coverage; and a
``data_dictionary.md`` beside it giving, per table, every column's dtype, unit,
role and a sample value.

Any folder under the gold root that holds at least one table gets both files,
however deep it sits - a variant subdirectory (``01_eriksen_replication/2019c``) or
a scenario folder (``scenarios/health_only``) is described exactly like a
top-level approach folder.

The descriptions are read from the folder's methods document in
``docs/methods/replications/`` (looked up by the folder's top-level component,
so a year subfolder shares its approach's document), so the two cannot drift
apart; the table properties are measured from the files themselves, for the
same reason.

These conventions are asserted while writing and reported in each README:

* EXIOBASE industry and product codes carry **no** ``A_`` / ``C_`` prefix.
* Countries are ISO3; EXIOBASE regions with no ISO3 code carry their region
  name (``RoW Europe`` and the other four).
* Every table is a star-schema fact or summary: dimension columns, then the
  measure and its unit.

Run::

    HC_ANALYSIS_YEAR=2022 HC_BACKGROUND_TAG=_snacship \\
        PYTHONPATH=src python -m analysis.build_folder_metadata
"""

from __future__ import annotations

import gzip
import os
import re
from typing import Any

import pandas as pd

from analysis.constants import (ERIKSEN_ROOT, SCOPES_ROOT, UNLETTERED_VARIANTS,
                                VARIANTS, variant_config,
                                variant_description)
from paths import OUTPUT_DIR

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#: The eighteen per-layer write-ups now live as sections of one file rather
#: than one file per folder; each section is anchored ``<a id="rNN"></a>``
#: immediately before its ``## NN — Title (`data/gold/results/...`)`` heading,
#: where ``NN`` is the folder's own leading two-digit component.
METHODS = os.path.join(REPO, "docs", "methods", "replications.md")

#: Columns that identify a dimension rather than carry a measure.
DIMENSION_HINTS = (
    "country", "region", "sector", "industry", "product", "indicator", "unit",
    "scope", "scenario", "method", "year", "component", "function", "layer",
    "origin", "target", "model", "analysis", "quantity", "parameter", "species",
    "asset", "stressor", "damage", "source", "basis", "check", "defect",
    "release", "revision", "metric", "item", "risk", "test", "verdict",
    "group", "note",
)

ROW_REGIONS = ("RoW Asia and Pacific", "RoW America", "RoW Europe",
               "RoW Africa", "RoW Middle East")


def _is_measure_dtype(dtype: Any) -> bool:
    """Whether a column of this dtype can carry a numeric measure.

    ``pandas.api.types.is_numeric_dtype`` returns ``True`` for boolean
    columns (bool is a numpy integer subtype), which would otherwise call
    every ``is_*`` / ``has_*`` flag a measure. A measure is a quantity, and a
    boolean is not one, so it is excluded here explicitly.

    Parameters
    ----------
    dtype : Any
        A pandas or numpy column dtype, as returned by ``Series.dtype``.

    Returns
    -------
    bool
        ``True`` if numeric and not boolean.
    """
    return (pd.api.types.is_numeric_dtype(dtype)
            and not pd.api.types.is_bool_dtype(dtype))


#: Shared material folded in from the hand-written
#: ``00_core_footprint/README_data_dictionary.md`` (now superseded by this
#: generator): the column vocabulary, region coding and the reconciliation
#: identity are properties of every gold table, not just that one folder's, so
#: every generated ``data_dictionary.md`` carries them rather than losing them
#: when the generator started claiming that filename.
COMMON_COLUMNS: tuple[str, ...] = (
    "## Common columns",
    "",
    "Every gold table shares this vocabulary; columns particular to one table",
    "are described below, per table.",
    "",
    "| Column | Meaning |",
    "|:---|:---|",
    "| `analysis_year` | year of the Danish expenditure data and of the MRIO background |",
    "| `model` | MRIO release actually used (e.g. `EXIOBASE v3.8.2 IOT_2022_ixi with Danish sea-transport reallocation (Rørmose Jensen & Iliev 2022)`) - **not** v3.10.2, which this study rejects (see `docs/methods/exiobase_release_and_classification.md`) |",
    "| `scenario` | model scenario (`baseline`, scope variants, pharma-mapping variants) |",
    "| `consuming_country_iso3` | always `DNK` - Denmark is the final consumer in this study |",
    "| `demand_component` | `healthcare_services`, `pharmaceuticals`, `medical_appliances` |",
    "| `indicator` | `climate_change`, `material_extraction`, `blue_water_consumption`, `land_use`, `waste_generation` |",
    "| `unit` | `kt CO2eq`, `kt`, `Mm3`, `km2`, or `M.EUR` for monetary rows |",
    "| `value` | numeric value in `unit` |",
    "",
    "## Country and region coding",
    "",
    "`*_country_iso3` uses **ISO 3166-1 alpha-3** for the 44 EXIOBASE countries.",
    "The five rest-of-world regions are **not countries** and keep their own",
    "codes and names: `WA` RoW Asia and Pacific, `WL` RoW America, `WE` RoW",
    "Europe, `WF` RoW Africa, `WM` RoW Middle East. `*_world_region` gives the",
    "continental grouping (Europe, Asia and Pacific, America, Middle East,",
    "Africa, Denmark).",
    "",
    "## The two perspectives (and why they reconcile)",
    "",
    "Every impact cell is $E_{ij} = s_i\\,L_{ij}\\,y_{H,j}$: pressure arising",
    "in node *i* caused by Danish healthcare final demand for node *j*. Summing",
    "over *i* gives the **consumption / contribution** perspective (by",
    "purchased product); summing over *j* gives the **production / hotspot**",
    "perspective (by producing node). Both are marginals of the same array, so",
    "they sum to the identical total - verified to machine precision by",
    "`analysis.validate_io_identities` (tests T5/T6). Allocating production",
    "emissions to final demand is additive and does not double count (Wood et",
    "al. 2018); embodied-flow tables ($\\mathbf{E}_Z$) would.",
    "",
    "## Units",
    "",
    "Monetary values are **million euro (M.EUR)** - EXIOBASE's native unit",
    "(`unit.txt` of the release). No US-dollar values are used anywhere in this",
    "model; dollar figures appearing in the comparative literature (Karliner et",
    "al. 2019, Lenzen et al. 2020, Pichler et al. 2019) are those studies' own",
    "units and are labelled as such wherever they are quoted.",
    "",
)

#: Hand-written knowledge that a regeneration must not erase, keyed by the
#: folder's *top-level* component (so a year or scenario subfolder inherits
#: its approach's note, the same lookup `_methods_summary` uses). A full
#: rewrite of `data_dictionary.md` on every run means anything a human needs
#: preserved has to live here rather than be edited into the generated file
#: directly - it would simply be overwritten on the next run. Restored
#: verbatim from the hand-written `00_core_footprint/README_data_dictionary.md`
#: this generator superseded (`git show 5a007a5:data/gold/results/00_core_footprint/README_data_dictionary.md`).
NOTES: dict[str, str] = {
    "00_core_footprint": (
        "## Important note on `healthcare_services`\n"
        "\n"
        "Following Steenmeijer et al. (2022), the healthcare-services component enters\n"
        "the model as the **scaled intermediate-input column** of the Danish\n"
        "\"Health and social work\" industry: value added (wages, surplus) carries no\n"
        "environmental pressure and is therefore not part of `y_H`. Consequently\n"
        "`sum(y_H)` is smaller than total health expenditure; `expenditure_summary.csv`\n"
        "reports both so the relationship is explicit. Pharmaceuticals and appliances\n"
        "enter at their full basic-price value, distributed over supplying regions.\n"
        "\n"
        "## Important note on `footprint_bilateral_producer_x_purchase.csv.gz`\n"
        "\n"
        "This table is **deliberately truncated**: it reports only the largest cells,\n"
        "covering >=99.5% of each total, plus an explicit `BELOW_THRESHOLD_REMAINDER`\n"
        "row per indicator x demand component so every total still reconciles exactly.\n"
        "`_bilateral_coverage.csv` in this folder reports the achieved coverage of the\n"
        "named cells. The untruncated marginals - `footprint_by_producing_node.csv`\n"
        "and `footprint_by_purchased_product.csv` - are complete."
    ),
}

#: The readme-side twin of :data:`NOTES`, keyed the same way and rendered into
#: `readme.md` instead of `data_dictionary.md`.
#:
#: Both files are rewritten in full on every run, so anything a reader needs
#: preserved has to live in this module. The two dictionaries are kept apart
#: because the two files answer different questions: the dictionary says what a
#: column means, the readme says what the folder is, where its figures are, and
#: where its numbers came from. A note that belongs in one rarely belongs in
#: the other.
#:
#: Rendered after the layer's question and its link into the methods document,
#: and before the conventions table.
README_NOTES: dict[str, str] = {
    "04_uncertainty_lenzen_ieooc": (
        "## Ranges on the reported estimates, not only on the total\n"
        "\n"
        "`uncertainty_by_group.csv` carries the mean, standard deviation,\n"
        "coefficient of variation and 95 % interval of every contribution group\n"
        "in every indicator - 90 rows - beside the interval on that group's\n"
        "SHARE of the footprint. The two answer different questions and the\n"
        "second cannot be derived from the first.\n"
        "\n"
        "Reviewer 1 asked for \"the resulting ranges for the main impact\n"
        "estimates\". A range on the total alone does not answer that: the\n"
        "groups do not vary independently, so a reader cannot infer a group's\n"
        "range from the total's. They share the MRIO multiplier, which is why\n"
        "seven of the nine climate groups carry a coefficient of variation of\n"
        "8.4 % - the MRIO block's own - and why their shares are far tighter\n"
        "than their levels: the shared factor cancels in the ratio.\n"
        "\n"
        "Two groups are not like the others, and that is the finding. Individual\n"
        "travel carries a CV of **26.3 %** against the 8.4 % of the MRIO-driven\n"
        "groups, because commuting and patient and visitor travel are bottom-up\n"
        "terms with uncertainties of their own rather than a share of the MRIO\n"
        "block; operational impacts carries 9.1 % for the same reason, smaller\n"
        "because the direct-emissions account is tighter. In share terms\n"
        "pharmaceuticals run 33.9 % to 39.4 % while individual travel runs\n"
        "8.4 % to 20.9 %, so the statement that pharmaceuticals lead is robust\n"
        "and the position of travel in the ranking is not - which is what\n"
        "`uncertainty_ranking_probabilities.csv` quantifies."
    ),
    "06_benchmarks_validation": (
        "## Reading `figaro_dk_footprint_by_origin.csv` without double counting\n"
        "\n"
        "`is_aggregate` marks only the three `c_orig` codes that overlap their\n"
        "own members - `WORLD`, `EU27_2020` and `EXT_EU27_2020` - read from\n"
        "`data/silver/eurostat_figaro/figaro_dimensions.csv`. `WRL_REST`, the\n"
        "residual for the countries FIGARO does not resolve individually, is\n"
        "**not** an aggregate and belongs in a sum over origins: the 49\n"
        "countries plus `WRL_REST` reproduce the `WORLD` row to every published\n"
        "digit in 2021, 2022 and 2023, and summing every row returns exactly\n"
        "three times it. Dropping every code without an ISO alpha-2 spelling\n"
        "would lose 7,393 kt CO2-eq in 2022, 13 % of the Danish footprint."
    ),
    "02_scopes_wood_hertwich/2019a": (
        "## Which model run this folder is\n"
        "\n"
        "Variant a: the submitted configuration. Its partition closes on\n"
        "`01_eriksen_replication/2019a`, and its transport share is the\n"
        "measurement that matters here - 34.94 % of this folder's climate\n"
        "total by producing node, against the 46 % the submitted manuscript\n"
        "reports and the 46.87 % that `2019_uncorrected` returns on v3.8.2.\n"
        "The submitted number is reproduced by the v3.8.2 run, not by the\n"
        "v3.7 one, which is the finding this variant exists to establish."
    ),
    "02_scopes_wood_hertwich/2019b": (
        "## Which model run this folder is\n"
        "\n"
        "Variant b isolates the Danish sea-transport correction on the\n"
        "submitted release: everything is variant a except the correction. The\n"
        "transport share falls from 34.94 % to 16.56 % and this folder's\n"
        "climate total from 8,693.84 to 6,624.71 kt CO2-eq, so on v3.7 as on\n"
        "v3.8.2 the correction is the larger of the two effects on the\n"
        "transport finding."
    ),
    "02_scopes_wood_hertwich/2019c": (
        "## Which model run this folder is\n"
        "\n"
        "Variant c for 2019: reference year 2019 on EXIOBASE v3.8.2\n"
        "`IOT_2016_ixi`, with the Danish sea-transport reallocation applied.\n"
        "Its partition closes on `01_eriksen_replication/2019c` exactly: the\n"
        "climate `TOTAL` of 4,107.334735 kt CO2-eq plus the self-supply loop of\n"
        "1.927600 kt is the grand total of 4,109.262335 kt that\n"
        "`scopes_summary.csv` publishes there.\n"
        "\n"
        "The bottom-up items are 2019's own: anaesthetic gases 12.470055 kt,\n"
        "commuting 327.944600 kt, patient and visitor travel 293.475319 kt.\n"
        "\n"
        "## The climate column of this folder moved on 11 September 2026\n"
        "\n"
        "The grand total was 4,054.772061 kt until the 2016 corrected\n"
        "background was rebuilt. That value was the IPCC AR4 characterisation\n"
        "of this same background: only the climate row of the characterisation\n"
        "matrix changed, and every other indicator in this folder is unmoved.\n"
        "See `docs/revision/defects_and_fixes.md`."
    ),
    "02_scopes_wood_hertwich/2019_uncorrected": (
        "## Which model run this folder is\n"
        "\n"
        "Reference year 2019 on EXIOBASE v3.8.2 `IOT_2016_ixi` with the Danish\n"
        "sea-transport reallocation **not** applied - and therefore **not**\n"
        "variant a, which is on v3.7. Its partition closes on\n"
        "`01_eriksen_replication/2019_uncorrected` exactly: the climate `TOTAL`\n"
        "of 6,416.930810 kt CO2-eq plus the self-supply loop of 1.927891 kt is\n"
        "the grand total of 6,418.858701 kt published there.\n"
        "\n"
        "This folder was withheld until 11 September 2026 on the grounds that\n"
        "the uncorrected and corrected 2016 model objects descended from two\n"
        "different extractions of `IOT_2016_ixi`. That diagnosis was wrong. One\n"
        "extraction ever existed - the two objects' `A`, `Y`, `R`, `H` and `x`\n"
        "are byte-identical - and what differed was the climate row of the\n"
        "characterisation matrix, AR4 in one and AR6 in the other. With both\n"
        "backgrounds on IPCC AR6 the reconciliation identity closes to the last\n"
        "digit, so there is nothing left to withhold.\n"
        "\n"
        "What the correction is worth, read across this folder and `2019c`: the\n"
        "climate footprint falls from 6,416.93 to 4,107.33 kt and the transport\n"
        "industry group from 46.85 % of it to 21.17 %."
    ),
    "02_scopes_wood_hertwich/2019d": (
        "## Which model run this folder is\n"
        "\n"
        "Variant d for 2019: the widest boundary this study runs, on the 2016\n"
        "table. Child care joins health and elder care in the demand vector\n"
        "(`HC_SCOPE=zorg_en_welzijn`) and consumption of fixed capital is\n"
        "inside the Leontief inverse, built by\n"
        "`analysis.capital_endogenised_background` rather than applied as a\n"
        "factor afterwards. Its partition closes on\n"
        "`01_eriksen_replication/2019d`.\n"
        "\n"
        "Both boundary moves raise the footprint, from 4,109.26 kt at variant c\n"
        "to 5,977.78 kt here, so the comparison a reader should draw from this\n"
        "folder is with a comparator that also endogenises capital and also\n"
        "carries child care - Schmidt & Merciai (2023), not the manuscript's\n"
        "own headline."
    ),
    "02_scopes_wood_hertwich/2022c": (
        "## Which model run this folder is\n"
        "\n"
        "The manuscript's headline run: reference year 2022 on EXIOBASE v3.8.2\n"
        "`IOT_2022_ixi`, with the Danish sea-transport reallocation applied.\n"
        "Its partition closes on `01_eriksen_replication/2022c` exactly: the\n"
        "climate `TOTAL` of 4,673.633405 kt CO2-eq plus the self-supply loop of\n"
        "1.833254 kt is the grand total of 4,675.466659 kt published there.\n"
        "\n"
        "The double-counting ledger's MRIO decomposition row, 3,906.446070 kt,\n"
        "is `00_core_footprint`'s `healthcare_footprint_mrio` to six decimals,\n"
        "which is what audit check C19 tests."
    ),
    "02_scopes_wood_hertwich/2022d": (
        "## Which model run this folder is\n"
        "\n"
        "Variant d on the headline year: child care added to the demand vector\n"
        "and consumption of fixed capital endogenised inside the Leontief\n"
        "inverse. Its partition closes on `01_eriksen_replication/2022d`.\n"
        "\n"
        "This is the variant built to be comparable with Schmidt & Merciai\n"
        "(2023), whose 6,100 kt covers NACE Q including child care with capital\n"
        "endogenised. At 6,495.66 kt it is 6.5 % above them, on a full pipeline\n"
        "run rather than the 1.2111 post-hoc uplift that\n"
        "`06_benchmarks_validation` applies to the headline; the residual\n"
        "difference their model being consequential and ours attributional\n"
        "cannot be removed by any boundary adjustment and remains."
    ),
    "02_scopes_wood_hertwich/2022_uncorrected": (
        "## Which model run this folder is\n"
        "\n"
        "Reference year 2022 on EXIOBASE v3.8.2 `IOT_2022_ixi` with the Danish\n"
        "sea-transport reallocation **not** applied - the comparison run, not\n"
        "the headline, and not a lettered variant. Its partition closes on\n"
        "`01_eriksen_replication/2022_uncorrected` exactly: the climate `TOTAL`\n"
        "of 6,085.494934 kt CO2-eq plus the self-supply loop of 1.833390 kt is\n"
        "the grand total of 6,087.328324 kt published there.\n"
        "\n"
        "What the correction is worth, read across this folder and `2022c`: the\n"
        "climate footprint falls from 6,085.49 to 4,673.63 kt, and the\n"
        "transport industry group falls from 32.19 % of it to 14.87 %. The\n"
        "ledger's MRIO decomposition row moves from 5,318.307735 to\n"
        "3,906.446070 kt on the same comparison. Nothing in this folder is on\n"
        "the headline basis, and no manuscript number is taken from it.\n"
        "\n"
        "Its purpose is figures 3 to 6 of the `2022_uncorrected` figure\n"
        "variant. Until this layer carried the configuration in its folder\n"
        "name, those four figures were drawn from the shipping-corrected\n"
        "tables and were byte-identical to the corrected variant's."
    ),
    "13_steenmeijer_replication": (
        "## Where the Dutch numbers come from\n"
        "\n"
        "Every `nl_*.csv` here is a conversion of the authors' own published\n"
        "output, not a re-run of their model. The source of record is the RIVM\n"
        "repository <https://github.com/rivm-syso/envr-footprint-healthcare>,\n"
        "kept verbatim at `archive/rivm_steenmeijer_2022/`; each row carries\n"
        "the workbook, the sheet and that URL in its own `source` column.\n"
        "`analysis.steenmeijer_replication.convert_rivm_outputs` regenerates\n"
        "them and asserts every column total back against the workbook it came\n"
        "from.\n"
        "\n"
        "The archive does not reproduce the article's own tables exactly: their\n"
        "script reads Statistics Netherlands at run time, so the direct\n"
        "emissions and the expenditure move with the release of the query. The\n"
        "differences, and two inconsistencies internal to the archive, are\n"
        "tabulated in the methods section linked above.\n"
        "\n"
        "## Figures\n"
        "\n"
        "Figures live in `figures/`, never in the data layer. These six render\n"
        "the article's figures 1, 2 and 3 for both countries in one style, so\n"
        "the two can be set side by side:\n"
        "\n"
        "| Figure | Caption |\n"
        "|:---|:---|\n"
        "| [`steenmeijer_fig1_contribution_nl.tiff`]"
        "(../../../../figures/steenmeijer_replication/"
        "steenmeijer_fig1_contribution_nl.tiff) | Contribution analysis of the "
        "Dutch health-care impact footprints by product group, 2016. Scopes "
        "follow the Greenhouse Gas Protocol. Rendered from the archived RIVM "
        "outputs in the groups, legend order and palette of Steenmeijer et al. "
        "(2022) figure 1. |\n"
        "| [`steenmeijer_fig1_contribution_dk.tiff`]"
        "(../../../../figures/steenmeijer_replication/"
        "steenmeijer_fig1_contribution_dk.tiff) | The same figure for Denmark, "
        "2022, shipping-corrected. This study's own `Transport` and "
        "`Unallocated` groups are folded into the Dutch *other* so the two "
        "legends are identical. |\n"
        "| [`steenmeijer_fig2_hotspot_sector_nl.tiff`]"
        "(../../../../figures/steenmeijer_replication/"
        "steenmeijer_fig2_hotspot_sector_nl.tiff) | Sector hotspot analysis of "
        "the Dutch health-care impact footprints, 2016: where the pressure "
        "physically arises. The indirect impact of private travel is "
        "distributed proportionally among all groups, as in the original. |\n"
        "| [`steenmeijer_fig2_hotspot_sector_dk.tiff`]"
        "(../../../../figures/steenmeijer_replication/"
        "steenmeijer_fig2_hotspot_sector_dk.tiff) | The same figure for "
        "Denmark, 2022, shipping-corrected. |\n"
        "| [`steenmeijer_fig3_hotspot_region_nl.tiff`]"
        "(../../../../figures/steenmeijer_replication/"
        "steenmeijer_fig3_hotspot_region_nl.tiff) | Geographical hotspot "
        "analysis of the Dutch health-care impact footprints, 2016, in the six "
        "world regions of the DESIRE concordance. The indirect impact of "
        "private travel is distributed proportionally among all regions, as in "
        "the original. |\n"
        "| [`steenmeijer_fig3_hotspot_region_dk.tiff`]"
        "(../../../../figures/steenmeijer_replication/"
        "steenmeijer_fig3_hotspot_region_dk.tiff) | The same figure for "
        "Denmark, 2022, shipping-corrected, with Denmark in the home-country "
        "slot the Netherlands occupies above. |\n"
        "\n"
        "All six are produced by `r/plot_steenmeijer_replication.r` from the\n"
        "tables in this folder and in `01_eriksen_replication/`. None carries a\n"
        "title or a caption on the image: the captions are the table above."
    ),
}


def _note_for(notes: dict[str, str], folder: str) -> str:
    """Look a hand-written note up by folder, most specific key first.

    Layers that publish one folder per analysis year need a note per year --
    which variant of the background that year was built on, above all -- and a
    layer that publishes a single folder needs one note for the layer. Trying
    the full relative path before its top-level component serves both without
    a second dictionary.

    Parameters
    ----------
    notes : dict of str to str
        Either :data:`NOTES` or :data:`README_NOTES`.
    folder : str
        Gold folder name, relative to the gold root.

    Returns
    -------
    str
        The note, or the empty string when neither key is present.
    """
    key = folder.replace(os.sep, "/")
    if key in notes:
        return notes[key]
    return notes.get(key.split("/")[0], "")


def _folder_readme_note(folder: str) -> str:
    """Hand-written readme note for one folder, or ``""`` when it has none.

    Parameters
    ----------
    folder : str
        Gold folder name, relative to the gold root. The whole path is looked
        up first, so a year-scoped subfolder can carry its own note, and the
        top-level component second, exactly like :func:`_folder_notes`.

    Returns
    -------
    str
        The note, or the empty string.
    """
    return _note_for(README_NOTES, folder)


#: Folders whose tables are defined by an explicit DDL rather than (or beside)
#: a methods document, keyed the same way as :data:`NOTES` - by the folder's
#: top-level component. `star`'s CSVs and Parquet facts are generated by
#: `analysis.build_star_schema` against the contract in
#: `docs/methods/star_schema.sql`; `build_manifest.py`'s star row cites the
#: same file.
SCHEMA_DOCS: dict[str, str] = {
    "star": os.path.join(REPO, "docs", "methods", "star_schema.sql"),
}


def _folder_notes(folder: str) -> str:
    """Hand-written note for one folder, or ``""`` when it has none.

    Parameters
    ----------
    folder : str
        Gold folder name, relative to the gold root. The whole path is looked
        up first, then the top-level component, exactly like
        :func:`_folder_readme_note`.
    """
    return _note_for(NOTES, folder)


def _read_head(path: str, n: int = 400) -> tuple[pd.DataFrame, int]:
    """Read a table's head and count its rows without loading it whole.

    Parameters
    ----------
    path : str
        CSV, gzipped CSV, or Parquet. The large star-schema facts are Parquet,
        which carries its row count and schema in the footer, so neither needs
        reading the data.
    n : int, optional
        Rows to read for column inspection.

    Returns
    -------
    tuple
        ``(head_frame, total_rows)``.
    """
    if path.endswith(".parquet"):
        import pyarrow.parquet as pq

        handle = pq.ParquetFile(path)
        total = handle.metadata.num_rows
        head = next(handle.iter_batches(batch_size=min(n, max(total, 1)))) \
            .to_pandas() if total else handle.schema_arrow.empty_table().to_pandas()
        return head, total
    opener = gzip.open if path.endswith(".gz") else open
    head = pd.read_csv(path, nrows=n)
    with opener(path, "rt", encoding="utf-8", errors="ignore") as fh:
        total = sum(1 for _ in fh) - 1
    return head, max(total, 0)


def _methods_section(folder: str) -> str | None:
    """The body of one layer's section in ``replications.md``, or ``None``.

    Parameters
    ----------
    folder : str
        Gold folder name, e.g. ``"07_malik_replication"`` or a nested table
        folder such as ``"01_eriksen_replication/2019c"`` - the section is
        looked up by the top-level component's leading two-digit number,
        since a year or scenario subfolder shares its approach's section.
    """
    top = folder.split(os.sep)[0]
    num = top[:2]
    if not os.path.exists(METHODS):
        return None
    text = open(METHODS, encoding="utf-8").read()
    anchor = re.search(rf'<a id="r{re.escape(num)}"></a>\s*\n\s*## ', text)
    if not anchor:
        return None
    start = anchor.end() - len("## ")
    rest = re.search(r'\n<a id="r\d+"></a>', text[start + 1:])
    end = start + 1 + rest.start() if rest else len(text)
    return text[start:end]


def _methods_summary(folder: str) -> tuple[str, str]:
    """Pull the title and the 'question this layer answers' from the methods doc.

    Parameters
    ----------
    folder : str
        Gold folder name, e.g. ``"07_malik_replication"`` or a nested table
        folder such as ``"01_eriksen_replication/2019c"`` - the section is
        looked up by the top-level component, since a year or scenario
        subfolder shares its approach's section.

    Returns
    -------
    tuple of str
        ``(title, question)``; empty strings when no matching section exists.
    """
    section = _methods_section(folder)
    if section is None:
        return "", ""
    title = re.search(r"^## \d+ — (.+?)(?:\s*\(`[^`]+`\))?\s*$", section, re.MULTILINE)
    block = re.search(r"### Question this layer answers\s+(.+?)(?=\n### )",
                      section, re.DOTALL)
    question = ""
    if block:
        para = [p.strip() for p in block.group(1).strip().split("\n\n") if p.strip()]
        question = " ".join(para[0].split()) if para else ""
    return (title.group(1).strip() if title else ""), question


def describe_table(path: str) -> dict[str, object]:
    """Measure one table's properties.

    Parameters
    ----------
    path : str
        Full path to the table.

    Returns
    -------
    dict
        Name, rows, grain, dimension and measure columns, units, and the
        dimension coverage where the table is node-resolved.
    """
    head, rows = _read_head(path)
    cols = list(head.columns)
    # A measure is a column that carries a numeric quantity - full stop. Every
    # non-numeric column (string, boolean, datetime) is a dimension whatever
    # its name says: `treatment_code` and `capital_included` do not become
    # measures just because "treatment" and "capital" are not in
    # DIMENSION_HINTS (`not _is_measure_dtype`, first clause below, decides
    # this unconditionally; the hint match in the third clause is then
    # redundant for a non-numeric column, but is kept so the hint list stays
    # in active use rather than becoming a name-only relic).
    #
    # For a *numeric* column, only the explicit `*_id` suffix promotes it to
    # a surrogate-key dimension - the hint list is deliberately NOT widened
    # to numeric columns in general: tried, and reverted, because several of
    # the 35 hints are ordinary English words that also occur inside real
    # measures' names - `share_of_scope_pct`, `scenario_value`,
    # `group_imports_bndkk`, `sector_share_of_national_pct` all matched
    # "scope" / "scenario" / "group" / "sector" and would have been
    # mislabelled dimensions. A column such as `analysis_year` still ends up
    # with no unit regardless (see `_column_unit`'s narrower, suffix-anchored
    # name check); it keeps the `measure` role here rather than being forced
    # into `dimension` by an incidental name match.
    dims = [c for c in cols
            if not _is_measure_dtype(head[c].dtype)
            or c.endswith("_id")
            or (any(h in c.lower() for h in DIMENSION_HINTS)
                and not _is_measure_dtype(head[c].dtype))]
    measures = [c for c in cols if c not in dims]
    units = sorted(head["unit"].dropna().unique().tolist())[:6] if "unit" in cols else []

    coverage = ""
    ccol = next((c for c in cols if c.endswith("country_iso3")), None)
    scol = next((c for c in cols if c.endswith("sector_code")), None)
    if ccol and scol:
        coverage = (f"{head[ccol].nunique()}+ regions x {head[scol].nunique()}+ "
                    f"industries (sampled)")
    return {
        "name": os.path.basename(path),
        "rows": rows,
        "dims": dims,
        "measures": measures,
        "units": units,
        "coverage": coverage,
    }


def _folder_tables(fdir: str) -> list[str]:
    """Table filenames directly inside one gold folder, sorted.

    Parameters
    ----------
    fdir : str
        Full path to the folder.

    Returns
    -------
    list of str
        Filenames of tables (``.csv``, ``.csv.gz``, ``.parquet``) directly in
        ``fdir``, excluding any leading-underscore auxiliary file.
    """
    return sorted(f for f in os.listdir(fdir)
                 if f.endswith((".csv", ".csv.gz", ".parquet"))
                 and not f.startswith("_"))


def _relative_link(target: str, fdir: str) -> str:
    """A forward-slash relative path from ``fdir`` to ``target``.

    Both the manifest and the methods-document links are computed this way
    rather than with a hardcoded ``../`` count, so a nested folder (a year or
    scenario subdirectory) gets a link with the right number of steps.
    """
    return os.path.relpath(target, fdir).replace(os.sep, "/")


def write_folder_readme(folder: str) -> str | None:
    """Write ``readme.md`` for one gold folder.

    Parameters
    ----------
    folder : str
        Gold folder name, relative to the gold root. May contain path
        separators for a nested table folder, e.g.
        ``"01_eriksen_replication/2019c"`` or ``"scenarios/health_only"``.

    Returns
    -------
    str or None
        Path written, or ``None`` when the folder holds no tables.
    """
    fdir = os.path.join(str(OUTPUT_DIR), folder)
    tables = _folder_tables(fdir)
    if not tables:
        return None

    title, question = _methods_summary(folder)
    top = folder.split(os.sep)[0]
    # A variant folder states its configuration in its FIRST line. The folder
    # name says which variant it is; only the configuration says what that
    # means, and a reader who opens one of eight sibling folders should not have
    # to find the layer readme, the methods document or this module to learn
    # which EXIOBASE release, correction, care boundary and capital treatment
    # produced the numbers under it.
    configuration = variant_description(folder)
    heading = f"# {folder}" + (f" — {configuration}" if configuration else "")
    lines = [heading, ""]
    if title:
        lines += [f"**{title}**", ""]
    if question:
        lines += [question, ""]
    if _methods_section(folder) is not None:
        anchor = f"r{top[:2]}"
        lines += [f"Method, equations, and verification: "
                  f"[`docs/methods/replications.md`, section {top[:2]}]"
                  f"({_relative_link(METHODS, fdir)}#{anchor}).", ""]
    readme_note = _folder_readme_note(folder)
    if readme_note:
        lines += [readme_note, ""]
    schema_doc = SCHEMA_DOCS.get(top)
    if schema_doc and os.path.exists(schema_doc):
        schema_name = os.path.basename(schema_doc)
        lines += [f"Schema definition (DDL) these tables satisfy: "
                  f"[`docs/methods/{schema_name}`]"
                  f"({_relative_link(schema_doc, fdir)}).", ""]

    manifest_path = os.path.join(str(OUTPUT_DIR), "manifest_lineage.csv")
    lines += [
        "## Conventions",
        "",
        "| Item | Convention |",
        "|:---|:---|",
        "| Schema | star schema: dimension columns, then measure and unit |",
        "| Industry / product codes | EXIOBASE codes **without** the `A_` / `C_` prefix |",
        "| Countries | ISO3 (`DNK`, `DEU`, `ROU`) |",
        "| Regions without an ISO3 code | region name (`RoW Europe`, `RoW Africa`, ...) |",
        "| Monetary unit | M.EUR, EXIOBASE basic prices, unless a column says otherwise |",
        f"| Provenance | one row per file in `{_relative_link(manifest_path, fdir)}` |",
        "",
        "## Tables",
        "",
    ]

    for name in tables:
        d = describe_table(os.path.join(fdir, name))
        lines += [f"### `{d['name']}`", ""]
        bullets = [f"- **Rows:** {d['rows']:,}",
                   f"- **Format:** {'parquet (pyarrow, snappy)' if name.endswith('.parquet') else 'csv'}"]
        if d["coverage"]:
            bullets.append(f"- **Resolution:** {d['coverage']}")
        if d["units"]:
            bullets.append(f"- **Units:** {', '.join(d['units'])}")
        bullets.append(f"- **Dimensions:** {', '.join(f'`{c}`' for c in d['dims']) or 'none'}")
        bullets.append(f"- **Measures:** {', '.join(f'`{c}`' for c in d['measures']) or 'none'}")
        lines += bullets + [""]

    out = os.path.join(fdir, "readme.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    return out


#: A column named this way is a percentage of *something*, never a physical
#: quantity, whatever the table's own ``unit`` column says - `share_of_scope_pct`
#: and `healthcare_share_pct` are `%`, not `kt CO2eq`. Checked only for
#: numeric columns (see :func:`_column_unit`): a *string* column such as
#: `input_group_share_pct` is a category label that happens to carry that
#: suffix, not a percentage value, and a string never carries a unit anyway.
_PCT_SUFFIXES = ("_pct", "_percent", "_share")


def _is_percentage_name(col: str) -> bool:
    """Whether a numeric column's name marks it as a percentage.

    Parameters
    ----------
    col : str
        Column name.

    Returns
    -------
    bool
        ``True`` if the (lower-cased) name ends in one of ``_PCT_SUFFIXES``
        or contains ``"share"``. Meaningful only for numeric columns; see
        ``_column_unit``.
    """
    lc = col.lower()
    return lc.endswith(_PCT_SUFFIXES) or "share" in lc


#: Name patterns that never carry a physical unit, whatever the table's own
#: `unit` column says: identifiers, codes, calendar years, and row/column/
#: draw counts. Most numeric dimension columns are already caught by
#: `DIMENSION_HINTS` in `describe_table` (e.g. `analysis_year`, `*_id`); this
#: catches the rest - a numeric `industry_code`, or a count column such as
#: `n_stressor_rows` or `n_nonzero_factors`, which sit beside a `unit` column
#: in their own tables and would otherwise inherit it (e.g. "kt").
#:
#: Ratios belong here for the same reason. A dimensionless quantity that sits in
#: a table whose `unit` column varies by row was being labelled "varies by row",
#: which reads as "some physical unit, look it up" when the correct answer is
#: "none". `phi_applied` and its cross-check, the sea-transport target share,
#: are the live case: both are a share of one Danish quantity by another, in the
#: same currency, so the currency cancels.
_NO_UNIT_SUFFIXES = ("_id", "_year", "_code", "_count", "_rank", "_flag",
                     "_ratio", "_cross_check")
_NO_UNIT_NAMES = {"id", "year", "code", "count", "rank", "flag", "rows",
                   "columns", "draws", "index", "phi", "phi_applied", "ratio"}
_NO_UNIT_PREFIXES = ("n_",)


def _is_no_unit_name(col: str) -> bool:
    """Whether a column's name marks it as inherently dimensionless.

    Parameters
    ----------
    col : str
        Column name.

    Returns
    -------
    bool
        ``True`` if the (lower-cased) name is in ``_NO_UNIT_NAMES``, ends in
        one of ``_NO_UNIT_SUFFIXES``, or starts with one of
        ``_NO_UNIT_PREFIXES`` (identifiers, codes, years, counts, ranks,
        flags, and ratios).
    """
    lc = col.lower()
    return (lc in _NO_UNIT_NAMES
            or lc.endswith(_NO_UNIT_SUFFIXES)
            or lc.startswith(_NO_UNIT_PREFIXES))


def _column_unit(col: str, dtype: Any, dims: set[str], unit_of: str) -> str:
    """The unit for one column - only ever the unit that column itself
    carries, never the table's shared unit borrowed for an unrelated column.

    Parameters
    ----------
    col : str
        Column name.
    dtype : Any
        The column's pandas dtype, as returned by ``Series.dtype``.
    dims : set of str
        Columns this table classifies as dimensions (see `describe_table`).
    unit_of : str
        The table's own shared unit, read from its `unit` column: a single
        value, `"varies by row"` when more than one is present, or `""` when
        the table carries no `unit` column at all.

    Returns
    -------
    str
        `"%"` for a percentage-named numeric column; `""` for the `unit`
        column itself, any non-numeric column, any id/code/year/count/rank/
        flag-named column, or any column this table already calls a
        dimension; otherwise `unit_of` - and never a guess: a column this
        function cannot place is left empty, not given the table's unit by
        default.
    """
    if col == "unit":
        return ""
    if not _is_measure_dtype(dtype):
        # every string/bool/datetime column is a dimension, not a measure,
        # and carries no unit whatever its name says (`input_group_share_pct`
        # is a category label, not a percentage, despite the suffix)
        return ""
    if _is_percentage_name(col):
        return "%"
    if _is_no_unit_name(col) or col in dims:
        return ""
    return unit_of


def column_dictionary(path: str) -> list[dict[str, str]]:
    """Describe every column of one table.

    Parameters
    ----------
    path : str
        Full path to the table.

    Returns
    -------
    list of dict
        One entry per column: name, dtype, unit, role, and a sample value.
    """
    head, _ = _read_head(path)
    described = describe_table(path)
    dims = set(described["dims"])
    unit_of = ""
    if "unit" in head.columns:
        seen = head["unit"].dropna().unique().tolist()
        if len(seen) == 1:
            unit_of = seen[0]
        elif len(seen) > 1:
            unit_of = "varies by row"
        # else: the unit column is entirely empty - unit_of stays "" rather
        # than the previous behaviour of guessing "varies by row"
    entries = []
    for col in head.columns:
        sample = head[col].dropna()
        entries.append({
            "column": col,
            "dtype": str(head[col].dtype),
            "unit": _column_unit(col, head[col].dtype, dims, unit_of),
            "role": "dimension" if col in dims else "measure",
            "example": str(sample.iloc[0])[:40] if len(sample) else "",
        })
    return entries


def write_folder_dictionary(folder: str) -> str | None:
    """Write ``data_dictionary.md`` for one gold folder.

    Parameters
    ----------
    folder : str
        Gold folder name, relative to the gold root, exactly as accepted by
        :func:`write_folder_readme`.

    Returns
    -------
    str or None
        Path written, or ``None`` when the folder holds no tables.
    """
    fdir = os.path.join(str(OUTPUT_DIR), folder)
    tables = _folder_tables(fdir)
    if not tables:
        return None
    lines = [f"# {folder} - data dictionary", "",
             "One row per column of every table in this folder. Units are the",
             "table's own; `varies by row` means the table carries a `unit`",
             "column and the value is read from there.", ""]
    lines += list(COMMON_COLUMNS)
    notes = _folder_notes(folder)
    if notes:
        lines += [notes, ""]
    lines += ["## Tables", ""]
    for name in tables:
        lines += [f"### `{name}`", "",
                  "| Column | Role | Type | Unit | Example |",
                  "|:---|:---|:---|:---|:---|"]
        for e in column_dictionary(os.path.join(fdir, name)):
            lines.append(f"| `{e['column']}` | {e['role']} | {e['dtype']} | "
                         f"{e['unit']} | {e['example']} |")
        lines.append("")
    out = os.path.join(fdir, "data_dictionary.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    return out


def write_variant_index(layer: str) -> str | None:
    """Write the variant index ``readme.md`` at the root of a variant layer.

    The layer folder itself holds no tables, so
    :func:`write_folder_readme` never reaches it, and a reader arriving at
    ``01_eriksen_replication/`` used to find eight sibling subfolders and
    nothing saying what distinguished them. This writes that one page: the
    four-variant definition table, the configurations published outside it, and
    one line per folder on disk.

    Parameters
    ----------
    layer : str
        Variant-scoped layer name, e.g. ``"01_eriksen_replication"``.

    Returns
    -------
    str or None
        Path written, or ``None`` when the layer is absent from this working
        copy.
    """
    fdir = os.path.join(str(OUTPUT_DIR), layer)
    if not os.path.isdir(fdir):
        return None
    present = sorted(d for d in os.listdir(fdir)
                     if os.path.isdir(os.path.join(fdir, d)))
    title, _ = _methods_summary(layer)
    lines = [f"# {layer}", ""]
    if title:
        lines += [f"**{title}**", ""]
    lines += [
        "Results are held one folder per model VARIANT, named `<year><letter>`.",
        "A variant fixes all four axes that change the numbers, so no two runs",
        "can overwrite each other and no reader has to infer which release or",
        "correction a folder carries:",
        "",
        "| Variant | EXIOBASE release | Danish shipping correction | Boundary | Capital |",
        "|:---|:---|:---|:---|:---|",
    ]
    for letter in sorted(VARIANTS):
        cfg = variant_config(letter)
        lines.append(f"| {letter} | {cfg['release_label']} | {cfg['shipping']} "
                     f"| {cfg['boundary']} | {cfg['capital']} |")
    lines += [
        "",
        "Variant a is the configuration the manuscript was submitted on, and",
        "variant d is the one built to be comparable with a comparator that",
        "endogenises capital and carries child care. The letters are resolved by",
        "`analysis.constants.variant_folder` in Python and `variant_name()` in",
        "`r/_dk_common.r`; nothing re-derives a folder name of its own.",
        "",
        "EXIOBASE v3.7 publishes no 2022 table - its series ends at 2016 - so",
        "the 2022 series has no a or b variant, and cannot be given one.",
        "",
        "## Folders in this working copy",
        "",
        "| folder | configuration |",
        "|:---|:---|",
    ]
    for name in present:
        lines.append(f"| [`{name}`]({name}/readme.md) | "
                     f"{variant_description(name) or 'not a variant folder'} |")
    unlettered = [n for n in present if n in UNLETTERED_VARIANTS]
    if unlettered:
        lines += [
            "",
            "## Folders outside the lettered scheme",
            "",
            "These keep a self-describing name rather than being given a letter",
            "they were not assigned. Both are EXIOBASE v3.8.2 without the",
            "Danish sea-transport correction, so **neither is variant a**, which",
            "is on v3.7 - the release the submitted manuscript used.",
            "",
        ]
        lines += [f"- `{n}`: {UNLETTERED_VARIANTS[n]['summary']}"
                  for n in unlettered]
        lines.append("")
    if _methods_section(layer) is not None:
        lines += [
            f"Method, equations, and verification: "
            f"[`docs/methods/replications.md`, section {layer[:2]}]"
            f"({_relative_link(METHODS, fdir)}#r{layer[:2]}).", ""]
    out = os.path.join(fdir, "readme.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    return out


def _table_folders(root: str) -> list[str]:
    """Every folder holding at least one table, relative to the gold root.

    Parameters
    ----------
    root : str
        Gold results root, i.e. ``OUTPUT_DIR``.

    Returns
    -------
    list of str
        Sorted relative paths (``os.sep``-joined), one per folder that holds
        at least one non-auxiliary ``.csv``, ``.csv.gz`` or ``.parquet`` file
        directly - a year or scenario subfolder counts on its own, its parent
        does not unless it also holds a table directly.
    """
    found = []
    for dirpath, _, names in os.walk(root):
        if any(n.endswith((".csv", ".csv.gz", ".parquet")) and not n.startswith("_")
               for n in names):
            rel = os.path.relpath(dirpath, root)
            found.append("" if rel == "." else rel)
    return sorted(f for f in found if f)


def main() -> None:
    """Write a readme and data dictionary into every gold folder holding a table.

    Plus the variant index at the root of each variant-scoped layer, which has
    no tables of its own to trigger the per-folder pass.
    """
    root = str(OUTPUT_DIR)
    folders = _table_folders(root)
    written = []
    for folder in folders:
        for fn in (write_folder_readme(folder), write_folder_dictionary(folder)):
            if fn:
                written.append(fn)
    # The two variant-scoped layers hold no tables at their own root, so the
    # loop above never reaches them; their index is what tells a reader what
    # the eight sibling folders under each of them are.
    for layer in (ERIKSEN_ROOT, SCOPES_ROOT):
        fn = write_variant_index(layer)
        if fn:
            written.append(fn)
    for path in written:
        print(f"  {os.path.relpath(path, root)}")
    print(f"\n{len(written)} files written across {len(folders)} table folders")


if __name__ == "__main__":
    main()
