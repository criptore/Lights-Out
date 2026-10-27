# Lights Out: Predicting Storm-Driven Power Outages and Recovery Across U.S. Counties

*ITE351 AI & Applications, Hanyang University, Fall 2026.*

## Group members

| Name | Organization | Email |
|---|---|---|
| Joshua HOORPAH | _Organization_ | _email_ |
| Thierry ROSANO | _Organization_ | _email_ |
| Erik Walter NIHLEN | _Organization_ | _email_ |
| Thomas LHUILLIER BETTIN | _Organization_ | _email_ |

## Research idea

When a storm hits the United States, some counties lose power for a few hours and others for weeks.
We want to know which county and storm features explain that difference. Using 672 FEMA-declared
storms from 2012 to 2026, we will train two supervised models at the county level. The first is a
classifier that flags major outages, defined as more than 10% of customers out at the peak
(`peak_share_out > 0.10`). The second is a regression model that predicts `hours_to_90pct_restored`,
the time needed to bring 90% of customers back. We will compare simple baselines (logistic and linear
regression) with tree ensembles such as random forests and gradient boosting. We will also test
whether satellite night light alone can detect an outage: the dataset authors report an AUC of only
about 0.52 to 0.57, barely above chance, and we will discuss why (generators, clouds, damaged
buildings). Finally, we will add wind speed and pressure from NOAA HURDAT2, joined on the NOAA storm
identifiers (for example AL022019), and measure how much they improve the models.

## Dataset

[Storm Blackout and Restoration](https://www.kaggle.com/datasets/heimdallresearch/storm-blackout)
v1.2 by Heimdall Research, CC BY 4.0. Sources and attribution are in [`data/NOTICE.md`](data/NOTICE.md).
