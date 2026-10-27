## Research use

These tables describe 672 past FEMA-declared U.S. storms, 2012-01-14 to 2026-08-11. They are
not for emergency decisions. Each question below has its own page, with pandas recipes, in `q1.md` to
`q8.md`.

The night-light result against reported outages is weak. County mean darkness (dark_county_mean) does not separate counties with large outages from counties with small ones: pooled AUC 0.515 over 418 storms and 5,841 counties, 95% interval 0.482 to 0.547 from resampling storms. The interval includes 0.5, which is chance. Lit-pixel radiance drop (dark_lit_ratio) separates counties with large outages from counties with small ones: pooled AUC 0.559 over 287 storms and 3,611 counties, 95% interval 0.511 to 0.605 from resampling storms. Change in the share of unlit lit-mask pixels (dark_lit_share) separates counties with large outages from counties with small ones: pooled AUC 0.566 over 287 storms and 3,611 counties, 95% interval 0.513 to 0.615 from resampling storms. An AUC of 0.5 is a coin flip, and
0.56 is a little better than a coin flip.

**How long do lights stay below normal?** `county_summary`, `days_to_normal`: median 20 (15 to 34) days over the
1,474 declared county rows that have it. The other rows give a reason code.

**Which storms had the largest outages?** `utility_by_county`, summed county peaks: Irma (AL112017), Helene (AL092024) and DR-4586.

**How long were customers out?** `utility_by_county`, `hours_to_90pct_restored`: median 30.25 hours over
7,297 rows. The tables hold county peaks only, with no storm-wide peak at one time.

**Which counties were declared, and how?** `declared_via`: 11,928 rows by major disaster declaration and
2,211 by the emergency declarations of 24 tropical storms.

**Tribal areas.** 47 storms have night light for 28 tribal areas. County rows for tribal-area storms are context: they describe the whole county, not the tribal area, and tribal nations are sovereign areas. The share fields say how much of each county lies inside the area.

**How much is missing?** 14 storms have no night light and 195 have no outage run, each with a
reason code.

**Comparing storms.** Radiance from different products should not be compared between storms; this release gives no conversion between them. 500 storms use VNP46A2 and 158 use VJ146A2.

**One row for Imelda.** Imelda is AL112019. FEMA DR-4466 is recorded in `storms.also_known_as`, so the
477 ids with an outage run are 477 storms.

**Imagery.** Before-and-after night-light pictures are not in this release.
Flood extent from Sentinel-1 radar is not in this release.
