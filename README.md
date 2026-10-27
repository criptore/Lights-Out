# Lights Out: Predicting Storm-Driven Power Outages and Recovery Across U.S. Counties

*ITE351 AI & Applications, Hanyang University, Fall 2026. Group project blog.*

This page is the blog for our final project. We follow Option A of the assignment: a step-by-step
machine-learning analysis of one dataset, in the spirit of Kaggle's Titanic tutorial. We will add
each step of the work here as it is done.

## Task 1: Group members

| Name | Organization | Email |
|---|---|---|
| Joshua HOORPAH | _Organization_ | _email_ |
| Thierry ROSANO | _Organization_ | _email_ |
| Erik Walter NIHLEN | _Organization_ | _email_ |
| Thomas LHUILLIER BETTIN | _Organization_ | _email_ |

## Task 3: Research idea

**Title:** Lights Out: Predicting Storm-Driven Power Outages and Recovery Across U.S. Counties

**Proposal:** When a storm hits the United States, some counties lose power for a few hours and
others for weeks. We want to know which county and storm features explain that difference. Using
672 FEMA-declared storms from 2012 to 2026, we will train two supervised models at the county
level. The first is a classifier that flags major outages, defined as more than 10% of customers
out at the peak (`peak_share_out > 0.10`). The second is a regression model that predicts
`hours_to_90pct_restored`, the time needed to bring 90% of customers back. We will compare simple
baselines (logistic and linear regression) with tree ensembles such as random forests and gradient
boosting. We will also test whether satellite night light alone can detect an outage: the dataset
authors report an AUC of only about 0.52 to 0.57, barely above chance, and we will discuss why
(generators, clouds, damaged buildings). Finally, we will add wind speed and pressure from NOAA
HURDAT2, joined on the NOAA storm identifiers (for example AL022019), and measure how much they
improve the models.

## Dataset

[Storm Blackout and Restoration](https://www.kaggle.com/datasets/heimdallresearch/storm-blackout),
version 1.2, by Heimdall Research (DOI [10.5281/zenodo.23010005](https://doi.org/10.5281/zenodo.23010005)).

The dataset covers 672 FEMA-declared U.S. storms with landfall or incident dates from 2012-01-14 to
2026-08-11. It joins two very different views of the same blackouts:

- **Night light from space.** NASA Black Marble (VIIRS) radiance for each county and night, with a
  baseline before the storm and recovery measures after it (`status`, `days_to_50`, `days_to_normal`).
- **Outages reported by utilities.** DOE EAGLE-I county records (from 2014-11-01 onward): peak
  customers out, share of customers out, customer-hours and restoration times.

The files we use are in [`data/`](data/):

| File | Rows | Content |
|---|---|---|
| `storms.csv` | 672 | One row per storm: id, name, type, landfall date, states |
| `county_summary.csv` | 51,493 | One row per storm and county: night-light summary plus the joined utility outage columns |
| `utility_by_county.csv` | 11,686 | One row per storm and declared county with an outage run: `peak_share_out`, `hours_to_90pct_restored`, … |
| `validation_pooled.csv` | 51 | The authors' AUC of night-light measures against reported outages, pooled and by product, storm type and year |

Column meanings are in [`data/DATA_DICTIONARY.md`](data/DATA_DICTIONARY.md) and known limits in
[`data/LIMITS.md`](data/LIMITS.md). An empty cell is never a zero: each empty value has a `*_reason`
column that says why it is missing. The 3 GB `county_daily.csv` (one row per county and night) is
not in this repository; download it from Kaggle if needed.

Things to keep in mind from the first look:

- Only 36 storms have a NOAA identifier (35 `AL…` and 1 `EP…`); the other 636 are FEMA numbers
  (`DR-…`), mostly severe storms and floods. The HURDAT2 enrichment therefore only applies to the
  tropical storms.
- `peak_share_out` is known for 9,989 county rows, and about half of them are above 10%.
- `hours_to_90pct_restored` is known for 7,297 rows, with a median of 30.25 hours and a long tail
  up to about 1,000 hours.

## Progress

| Step | Notebook | Status |
|---|---|---|
| 1. Exploratory data analysis | | To do |
| 2. Major-outage classifier | | To do |
| 3. Restoration-time regression | | To do |
| 4. Night light as an outage detector | | To do |
| 5. NOAA HURDAT2 wind and pressure | | To do |

To run the notebooks:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## License and attribution

The dataset is published by Heimdall Research under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), which allows reuse and redistribution with
attribution. Its inputs keep their own terms: NASA Black Marble VNP46A2 and VJ146A2 (NASA open data
policy, Roman et al. 2018, DOI 10.1016/j.rse.2018.03.017), EAGLE-I / ORNL outage records (CC BY 4.0,
DOI 10.6084/m9.figshare.24237376), and public-domain data from EIA, the U.S. Census Bureau, OpenFEMA
and NOAA NHC. See [`data/NOTICE.md`](data/NOTICE.md) and [`data/CITATION.cff`](data/CITATION.cff).
The data is not for real-time emergency response or for decisions about a single address or property.
