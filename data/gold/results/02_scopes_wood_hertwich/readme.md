# 02_scopes_wood_hertwich

**GHG-Protocol scope decomposition**

Results are held one folder per model VARIANT, named `<year><letter>`.
A variant fixes all four axes that change the numbers, so no two runs
can overwrite each other and no reader has to infer which release or
correction a folder carries:

| Variant | EXIOBASE release | Danish shipping correction | Boundary | Capital |
|:---|:---|:---|:---|:---|
| a | v3.7 | no | health care | excluded |
| b | v3.7 | yes | health care | excluded |
| c | v3.8.2 | yes | health care | excluded |
| d | v3.8.2 | yes | health care plus child and elder care | endogenised |

Variant a is the configuration the manuscript was submitted on, and
variant d is the one built to be comparable with a comparator that
endogenises capital and carries child care. The letters are resolved by
`analysis.constants.variant_folder` in Python and `variant_name()` in
`r/_dk_common.r`; nothing re-derives a folder name of its own.

EXIOBASE v3.7 publishes no 2022 table - its series ends at 2016 - so
the 2022 series has no a or b variant, and cannot be given one.

## Folders in this working copy

| folder | configuration |
|:---|:---|
| [`2016_uncorrected`](2016_uncorrected/readme.md) | EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - the 2016 counterpart of 2019_uncorrected and 2022_uncorrected |
| [`2016a`](2016a/readme.md) | EXIOBASE v3.7, no Danish shipping correction, health-care boundary, capital excluded - the submitted configuration |
| [`2016b`](2016b/readme.md) | EXIOBASE v3.7, Danish shipping correction, health-care boundary, capital excluded |
| [`2016c`](2016c/readme.md) | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| [`2016d`](2016d/readme.md) | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |
| [`2019_uncorrected`](2019_uncorrected/readme.md) | EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - not variant a, which is on v3.7 |
| [`2019a`](2019a/readme.md) | EXIOBASE v3.7, no Danish shipping correction, health-care boundary, capital excluded - the submitted configuration |
| [`2019b`](2019b/readme.md) | EXIOBASE v3.7, Danish shipping correction, health-care boundary, capital excluded |
| [`2019c`](2019c/readme.md) | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| [`2019d`](2019d/readme.md) | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |
| [`2022_uncorrected`](2022_uncorrected/readme.md) | EXIOBASE v3.8.2 IOT_2022_ixi, no Danish shipping correction, health-care boundary, capital excluded |
| [`2022c`](2022c/readme.md) | EXIOBASE v3.8.2, Danish shipping correction, health-care boundary, capital excluded - the headline configuration |
| [`2022d`](2022d/readme.md) | EXIOBASE v3.8.2, Danish shipping correction, health care plus child and elder care, capital endogenised |

## Folders outside the lettered scheme

These keep a self-describing name rather than being given a letter
they were not assigned. Both are EXIOBASE v3.8.2 without the
Danish sea-transport correction, so **neither is variant a**, which
is on v3.7 - the release the submitted manuscript used.

- `2016_uncorrected`: EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - the 2016 counterpart of 2019_uncorrected and 2022_uncorrected
- `2019_uncorrected`: EXIOBASE v3.8.2 IOT_2016_ixi, no Danish shipping correction, health-care boundary, capital excluded - not variant a, which is on v3.7
- `2022_uncorrected`: EXIOBASE v3.8.2 IOT_2022_ixi, no Danish shipping correction, health-care boundary, capital excluded

Method, equations, and verification: [`docs/methods/replications.md`, section 02](../../../../docs/methods/replications.md#r02).
