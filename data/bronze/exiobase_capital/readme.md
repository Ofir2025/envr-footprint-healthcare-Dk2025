# EXIOBASE capital-formation matrix

The capital matrix $\mathbf{K}$ used to endogenise capital consumption in the
footprint, following Södersten, Wood & Hertwich. It is what the
capital-boundary comparison in `data/gold/results/11_capital_gfcf/` is built on.

| item | value |
|:---|:---|
| Provider | Södersten, Wood & Hertwich, NTNU Industrial Ecology Programme |
| Dataset | EXIOBASE capital-formation matrices, product-by-industry, consumption-of-fixed-capital variant |
| DOI | `10.5281/zenodo.7073276` |
| URL | <https://zenodo.org/record/7073276> |
| Citation | Södersten, Wood & Hertwich (2018) *Environ Sci Technol* 52:13250-13259, doi `10.1021/acs.est.8b02791` |
| Licence | CC BY 4.0 |
| Retrieved | wired in 2026-09-08 (`ab24cb8`) |

## Download step

The Zenodo record publishes one MATLAB file per release, year and variant.
Take the EXIOBASE v3.8.2 file for 2020, consumption-of-fixed-capital,
product-by-industry, and keep its published name:

```
Kbar_exio_v3_8_2_2020_cfc_pxi.mat
```

`analysis.capital_endogenised_sodersten` builds the path from `KBAR_YEAR`, so a
different year needs the matching file under the same name pattern.

| file | size | shape | unit |
|:---|:---|:---|:---|
| `Kbar_exio_v3_8_2_2020_cfc_pxi.mat` | 23.0 MB | 9800 products × 7987 industries, sparse | M.EUR |

Not a delimited file, so it has no column dictionary. The `.mat` holds a single
sparse array under the variable the module reads; the row index is the 49
regions × 200 products block structure and the column index the 49 regions ×
163 industries block structure of the same release.

**Caveat.** The matrix is for **2020** and the background model is the **2022**
table. The two years are carried as a known mismatch in the capital-boundary
comparison rather than reconciled: no v3.8.2 capital matrix is published for
2022. `analysis.capital_endogenised_sodersten` also needs
`MRSUT_2020/supply.csv` from the same EXIOBASE v3.8.2 store to convert the
product-by-industry matrix to industry-by-industry; that file is not mirrored
here and its path is a module constant.

**Not in version control.** 23 MB of third-party data. Re-download it from the
Zenodo record above.
