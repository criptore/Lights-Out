# Lights Out: Predicting Storm-Driven Power Outages and Recovery Across U.S. Counties

*ITE351 AI & Applications, Hanyang University, Fall 2026. Group project blog.*

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
`hours_to_90pct_restored`, the time needed to bring 90% of customers back. We will compare simple baselines (logistic and
linear regression) with tree ensembles such as random forests and gradient boosting. We will also test
whether satellite night light alone can detect an outage: the dataset authors report an AUC of
only about 0.55, barely above chance, and we will discuss why (generators, clouds, damaged
buildings). Finally, we will add wind speed and pressure from NOAA HURDAT2, joined on the NOAA
storm identifiers (for example AL022019), and measure how much they improve the models.

## Dataset

[Storm Blackout and Restoration](https://www.kaggle.com/datasets/heimdallresearch/storm-blackout)
v1.2 by Heimdall Research (DOI [10.5281/zenodo.23010005](https://doi.org/10.5281/zenodo.23010005)).
It covers 672 FEMA-declared U.S. storms from 2012-01-14 to 2026-08-11 and gives, for each storm and
county, two views of the same blackouts:

- **Night light from space:** NASA Black Marble (VIIRS) radiance before and after the storm.
- **Outages reported by utilities:** DOE EAGLE-I records (from 2014-11 onward): peak customers out,
  share of customers out, customer-hours and restoration times.

| File in [`data/`](data/) | Rows | Content |
|---|---|---|
| `storms.csv` | 672 | One row per storm: id, name, type, landfall date, states |
| `county_summary.csv` | 51,493 | One row per storm and county: night-light summary and outage columns |
| `utility_by_county.csv` | 11,686 | Reported outages per storm and county, with `peak_share_out` and `hours_to_90pct_restored` |
| `validation_pooled.csv` | 51 | The authors' AUC of night-light measures against reported outages |

Column meanings are in [`data/DATA_DICTIONARY.md`](data/DATA_DICTIONARY.md) and known limits in
[`data/LIMITS.md`](data/LIMITS.md). The 3 GB `county_daily.csv` is not in this repository.

License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Sources and attribution
(NASA Black Marble, EAGLE-I / ORNL, EIA, U.S. Census Bureau, OpenFEMA, NOAA NHC) are in
[`data/NOTICE.md`](data/NOTICE.md).
