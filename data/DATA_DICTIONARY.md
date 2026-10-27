# Data dictionary: Storm Blackout and Restoration, version 1.2

One entry per column of every table: its type, unit, meaning, and when it is empty and why. An empty cell means the value was not measured. It is never written as 0. Read the code columns (`geoid`, `region_id`, `area_id`, `context_for_region_id`, `county_geoid`, `state_fips`) as text to keep their leading zeros.

County rows for tribal-area storms are context: they describe the whole county, not the tribal area, and tribal nations are sovereign areas. The share fields say how much of each county lies inside the area.

Radiance from different products should not be compared between storms; this release gives no conversion between them. `product` says which one a storm uses.

## `storms.csv`

One row per storm, including the storms that have no night-light numbers or no outage run. Key: `event_id`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `name` | string |  | Storm name or FEMA declaration title | Never empty |
| `kind` | string |  | Storm type from the NHC record or the FEMA incident type. Values: `tropical`, `typhoon`, `winter_storm`, `severe_ice_storm`, `snowstorm`, `severe_storm`, `coastal_storm`, `straight-line_winds`, `tornado`, `flood` | Never empty |
| `landfall` | date |  | UTC date of the first HURDAT2 landfall on a U.S. state (the first on a territory when there was none on a state). For FEMA-numbered storms, the FEMA incident begin date | Never empty |
| `landfall_time_utc` | string |  | UTC time of that landfall, HH:MM | No landfall time in the source: FEMA-numbered storms, and tropical storms whose date comes from the catalog without a HURDAT2 landfall record |
| `first_impact_date` | date |  | UTC date the storm centre first came within 250 km of a county in the table, when that is two or more days before landfall. The baseline nights end before it | The storm reached no county two or more days before landfall |
| `states` | string |  | Declared states and territories, space separated | Never empty |
| `source` | string |  | Where the landfall date and time come from | Never empty |
| `night_light_unit` | string |  | county: night light by county. tribal_area: night light by tribal area, for a tribal declaration with no county named. Values: `county`, `tribal_area` | The storm has no night-light numbers. night_light_reason says why |
| `night_light_reason` | string |  | Why the storm has no night-light numbers. before_nasa_record: the storm window starts before the VNP46A2 record begins on 2012-01-19. territory_not_in_county_boundaries: Guam, the Northern Mariana Islands or American Samoa, which the county boundary file does not cover. Values: `before_nasa_record`, `territory_not_in_county_boundaries` | The storm has night-light numbers |
| `product` | string |  | Night-light product the storm is measured with: VNP46A2 (Suomi NPP) or VJ146A2 (NOAA-20). One product per storm. Radiance from different products should not be compared between storms. Values: `VNP46A2`, `VJ146A2` | The storm has no night-light numbers. night_light_reason says why |
| `outage_reason` | string |  | Why the storm has no county outage run. no_utility_record_before_2014: before the public EAGLE-I county series starts on 2014-11-01. no_published_year: no EAGLE-I file is published for the year. no_county_outage_record: a tribal declaration that names no county. territory_not_in_eaglei: a territory EAGLE-I does not cover. Values: `no_utility_record_before_2014`, `no_published_year`, `no_county_outage_record`, `territory_not_in_eaglei` | The storm has an outage run. Its rows are in utility_by_county |
| `window_note` | string |  | window_cut_at_source_end: the 45-day outage window runs past 31 December 2025, the last day of the published EAGLE-I record, so records stop there. Values: `window_cut_at_source_end` | The outage window is not cut, or the storm has no outage run |
| `also_known_as` | string |  | FEMA disaster numbers for the same storm that have no row of their own, space separated (for example DR-4466 on Imelda, AL112019). Each such declaration names the same counties on the same date, and its outage records are the same | No other number is recorded for the storm |

## `county_summary.csv`

One row per storm and county with night light (method v3), with the outage columns joined from utility_by_county. Key: `event_id`, `geoid`.
Every row joins `storms` on `event_id`, and holds the same `product`.
One product per storm: `product` is one value within each `event_id`.
A wind radius is on file for a storm or it is not: `in_nhc_wind_radius` is empty in every row or in none within each `event_id`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `geoid` | string |  | County FIPS code, 5 digits. Read as text to keep the leading zero | Never empty |
| `county` | string |  | County name | Never empty |
| `state` | string |  | State or territory postal code | Never empty |
| `declared` | boolean |  | True when FEMA declared the county for this storm | Never empty |
| `declared_via` | string |  | The declaration that names the county: major_disaster, or emergency for a tropical storm's emergency declaration. A county named in both is major_disaster. Values: `major_disaster`, `emergency` | The county is not declared for this storm |
| `in_nhc_wind_radius` | boolean |  | True when the county lies inside the NHC 34-knot wind radius of the storm, False when it lies outside | No wind radius is on file for the storm (filled for the 34 Atlantic storms HURDAT2 gives a radius for). Empty does not mean outside |
| `product` | string |  | Night-light product the storm is measured with: VNP46A2 (Suomi NPP) or VJ146A2 (NOAA-20). One product per storm. Radiance from different products should not be compared between storms. Values: `VNP46A2`, `VJ146A2` | Never empty |
| `baseline_radiance` | number | nW/cm²/sr | Median radiance of the clear baseline nights before the storm | baseline_source is insufficient: there were no baseline nights |
| `baseline_nights` | integer |  | Clear nights in the baseline | Never empty |
| `baseline_source` | string |  | event_window: baseline nights before the storm. prior_year: the same season a year earlier, used when the nights before the storm were too few. insufficient: no baseline. Values: `event_window`, `prior_year`, `insufficient` | Never empty |
| `post_obs_nights` | integer |  | Nights with usable pixels after the landfall date | Never empty |
| `median_valid_pixel_share` | number |  | Median share of usable pixels after the landfall date | Never empty |
| `status` | string |  | What the night-light series did. It is not a detected power outage. light_drop: smoothed light fell below the county's normal range soon after impact. no_measurable_outage: observed, no such fall (the name keeps an old use of the word outage for a night-light state). cloud_obscured: not observed until late and normal by then. low_signal: too noisy to judge. insufficient_data: too few nights. Values: `light_drop`, `no_measurable_outage`, `cloud_obscured`, `low_signal`, `insufficient_data` | Never empty |
| `outage_min_ratio` | number |  | Lowest smoothed light ratio after impact (a night-light value despite the name) | status is low_signal or insufficient_data |
| `outage_min_day` | integer | days | Day of that lowest ratio, counted from impact_date | status is low_signal or insufficient_data |
| `days_to_50` | integer | days | Days from impact until smoothed light was back at or above 50% of baseline | Not measured. days_to_50_reason says why |
| `days_to_50_reason` | string |  | Why days_to_50 is empty. never_below_50: a light_drop status, but light never fell below 50%. not_back_to_50_in_window: fell below 50% and did not return. no_outage_measured: observed, no light drop found (a night-light state despite the name). not_observed_cloud, not_observed_too_few_nights: the county was not observed. not_measurable_low_signal: its light is too noisy to judge. Values: `never_below_50`, `not_back_to_50_in_window`, `no_outage_measured`, `not_observed_cloud`, `not_observed_too_few_nights`, `not_measurable_low_signal` | days_to_50 has a value |
| `days_to_normal` | integer | days | Days from impact until smoothed light was back in the county's normal range | Not measured. days_to_normal_reason says why |
| `days_to_normal_reason` | string |  | Why days_to_normal is empty. not_back_to_normal_in_window: a light_drop status that did not return to normal. The other codes are as in days_to_50_reason. Values: `not_back_to_normal_in_window`, `no_outage_measured`, `not_observed_cloud`, `not_observed_too_few_nights`, `not_measurable_low_signal` | days_to_normal has a value |
| `recovery_uncertain` | boolean |  | True when a gap of 5 or more days without a clear night comes just before days_to_normal | days_to_normal is empty |
| `window_end_day` | integer | days | Last day of the night-light window, counted from impact_date | Never empty |
| `window_end_reason` | string |  | window: the full window. data_end: the stored nights stop earlier. next_storm:DR-number: the next FEMA storm in the county | Never empty |
| `impact_date` | date |  | Date the storm reached the county, day 0 of the window | Never empty |
| `impact_source` | string |  | How impact_date was chosen. track_within_250km: first UTC date the HURDAT2 track came within 250 km of the county. track_closest_approach: the track never came that close, so the date of closest approach. catalog_landfall: storms.landfall. Values: `track_within_250km`, `track_closest_approach`, `catalog_landfall` | Never empty |
| `clear_nights_pre` | integer |  | Clear nights before impact | Never empty |
| `clear_nights_post` | integer |  | Clear nights after impact | Never empty |
| `method_version` | string |  | Night-light method version. Values: `v3` | Never empty |
| `source_night_light` | string |  | Layer marker. Values: `night_light` | Never empty |
| `post_days_window` | integer | days | Days after the landfall date covered by stored nights | Never empty |
| `available` | boolean |  | True when utility records cover this county's window | Never empty |
| `reason` | string |  | Utility availability. ok: records in the window. no_rows_in_window: rows that year but none in the window. no_utility_record: no EAGLE-I rows for the county that year. county_not_declared: the outage run reads declared counties only. no_utility_record_before_2014, no_published_year: the storm-level outage_reason, for a storm with no outage run. Values: `ok`, `no_rows_in_window`, `no_utility_record`, `county_not_declared`, `no_utility_record_before_2014`, `no_published_year` | Never empty |
| `source` | string |  | utility_records when the county has EAGLE-I rows in the window, otherwise none. Values: `utility_records`, `none` | Never empty |
| `peak_customers_out` | number |  | Peak customers out reported in EAGLE-I, taken after readings that hold more than one collection snapshot are replaced (see flagged_readings). A replaced reading is an interpolated value that was not measured | No utility record for the county in the window. peak_reason is set and reason says why |
| `peak_reason` | string |  | Why peak_customers_out is empty: no_utility_record. reason gives the cause (for example county_not_declared). Values: `no_utility_record` | peak_customers_out has a value |
| `peak_customers_out_raw` | number |  | Highest reading in the window as the EAGLE-I year file records it, before any filter | peak_customers_out is empty |
| `flagged_readings` | integer |  | Readings in the window that held more than one collection snapshot and were replaced. 0 when none | peak_customers_out is empty |
| `peak_share_out` | number |  | peak_customers_out divided by customers_total | No share. peak_share_reason says why |
| `peak_share_reason` | string |  | Why peak_share_out is empty. no_utility_record: no EAGLE-I rows. no_customers_total: customers_total is empty and customers_reason says why. peak_above_customer_estimate: the peak is above the customer estimate. Values: `no_customers_total`, `no_utility_record`, `peak_above_customer_estimate` | peak_share_out has a value |
| `customer_hours_out` | number | customer-hours | Customer-hours out in the window from impact_date, or up to a reporting drop when customer_hours_reason is reporting_drop | peak_customers_out is empty |
| `hours_to_50pct_restored` | number | hours | Hours from the peak until customers out stayed at or below 50% of the peak for 6 hours | Not measured. hours_to_50pct_reason says why |
| `hours_to_50pct_reason` | string |  | Why hours_to_50pct_restored is empty. not_restored_in_window: still above half the peak at the end. no_customers_out: the peak is 0. no_utility_record: no EAGLE-I rows. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `not_restored_in_window`, `no_customers_out`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_to_50pct_restored has a value |
| `hours_to_90pct_restored` | number | hours | Hours from the peak until customers out stayed at or below 10% of the peak for 6 hours | Not measured. hours_to_90pct_reason says why |
| `hours_to_90pct_reason` | string |  | Why hours_to_90pct_restored is empty. not_restored_in_window: still above 10% of the peak at the end. no_customers_out: the peak is 0. no_utility_record: no EAGLE-I rows. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `not_restored_in_window`, `no_customers_out`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_to_90pct_restored has a value |
| `hours_under_1pct_customers` | number | hours | Hours from the peak until customers out stayed at or below 1% of customers_total for 6 hours | Not measured. hours_under_1pct_reason says why |
| `hours_under_1pct_reason` | string |  | Why hours_under_1pct_customers is empty. never_above_1pct: the outage never passed 1% of customers. not_under_1pct_in_window: still above 1% at the end. no_customers_total, peak_above_customer_estimate or no_utility_record: nothing to measure against. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `never_above_1pct`, `not_under_1pct_in_window`, `no_customers_total`, `peak_above_customer_estimate`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_under_1pct_customers has a value |
| `coverage_gap` | boolean |  | True when the utility series has a gap longer than 6 hours after the peak | peak_customers_out is empty |
| `customers_total` | number | customers | Estimated electric customers in the county: the state's EIA-861 customer count split across counties by Census housing units | No estimate. customers_reason says why |
| `customers_reason` | string |  | Why customers_total is empty. eia861_territory_incomplete, no_housing_units: the estimate could not be made for this county. outage_exceeds_*: the peak, after flagged readings are replaced, is above the estimate. The peak is published as reported, and the suffix says which other customer counts it also exceeds. no_outage_row: the county has no outage row, and the estimate comes with the outage run. Values: `eia861_territory_incomplete`, `no_housing_units`, `no_outage_row`, `outage_exceeds_customer_estimate`, `outage_exceeds_estimate_and_mcc`, `outage_exceeds_estimate_and_eaglei_total`, `outage_exceeds_every_customer_model` | customers_total has a value |
| `estimate_exceeded_in_other_storm` | boolean |  | True when this county's peak was above its customer estimate in another storm of the catalog. The share here then rests on an estimate that may be too low | Never empty |
| `customer_hours_reason` | string |  | reporting_drop: the integral stops at a one-step collapse of the utility feed. The tail of the window is not counted. Values: `reporting_drop` | The integral covers the window, or peak_customers_out is empty |
| `reporting_drop` | boolean |  | True when a restore hour is empty because the utility feed fell in one 15-minute step and did not come back. The answer to give is: The utility's outage feed stopped reporting for this county partway through, so a restoration time cannot be given. | peak_customers_out is empty |

## `county_daily.csv`

One row per storm, county and night. Key: `event_id`, `geoid`, `date`.
Every row joins `county_summary` on `event_id`, `geoid`, and holds the same `declared`, `declared_via`, `in_nhc_wind_radius`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `date` | date |  | Night of observation (the UTC date of the product file) | Never empty |
| `geoid` | string |  | County FIPS code, 5 digits. Read as text to keep the leading zero | Never empty |
| `declared` | boolean |  | True when FEMA declared the county for this storm. Same value as county_summary.declared | Never empty |
| `declared_via` | string |  | The declaration that names the county: major_disaster, or emergency for a tropical storm's emergency declaration. A county named in both is major_disaster. Values: `major_disaster`, `emergency` | The county is not declared for this storm |
| `in_nhc_wind_radius` | boolean |  | True when the county lies inside the NHC 34-knot wind radius of the storm, False when it lies outside | No wind radius is on file for the storm (filled for the 34 Atlantic storms HURDAT2 gives a radius for). Empty does not mean outside |
| `days_from_landfall` | integer | days | Days since storms.landfall (negative before). Stored nights reach back about 400 days where a prior-year baseline was read | Never empty |
| `radiance_nw_cm2_sr` | number | nW/cm²/sr | Mean radiance over the valid pixels that night: the sum of radiance over valid pixels divided by their number | valid_pixels is 0. A night with no valid pixel is never written as 0 |
| `valid_pixels` | integer | pixels | Valid pixels that night: a value, Mandatory_Quality_Flag 0, confident clear and no snow | Never empty |
| `valid_pixel_share` | number |  | valid_pixels as a share of all pixels in the area | Never empty |
| `snow_excluded_share` | number |  | Snow pixels as a share of pixels with a finite radiance. A different base from valid_pixel_share, so the two can add to more than 1 | Never empty |
| `light_ratio` | number |  | radiance_nw_cm2_sr divided by baseline_radiance of the summary row | radiance_nw_cm2_sr is empty, or the summary row has no baseline |
| `thin_night` | boolean |  | True when the night has 1 to 19 valid pixels. The radiance is kept as measured and is noisy | Never empty |

## `utility_by_county.csv`

Outage columns, one row per storm with an outage run and declared county. Key: `event_id`, `geoid`.
Every row joins `county_summary` (or else `declared_unmatched`) on `event_id`, `geoid`, and holds the same `declared`, `peak_customers_out`, `peak_share_out`, `customer_hours_out`, `customer_hours_reason`, `hours_to_50pct_restored`, `hours_to_90pct_restored`, `customers_total`, `reporting_drop`.
Every row joins `storms` on `event_id`, and holds the same `window_note`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `geoid` | string |  | County FIPS code, 5 digits. Read as text to keep the leading zero | Never empty |
| `county` | string |  | County name | The county is not in the boundary file (Bedford city, Virginia, 51515); its row is in declared_unmatched |
| `state` | string |  | State or territory postal code | Never empty |
| `declared` | boolean |  | True: the outage run reads declared counties only | Never empty |
| `available` | boolean |  | True when utility records cover this county's window | Never empty |
| `reason` | string |  | Utility availability. ok: records in the window. no_rows_in_window: rows that year but none in the window. no_utility_record: no EAGLE-I rows for the county that year. Values: `ok`, `no_rows_in_window`, `no_utility_record` | Never empty |
| `source` | string |  | utility_records when the county has EAGLE-I rows in the window, otherwise none. Values: `utility_records`, `none` | Never empty |
| `peak_customers_out` | number |  | Peak customers out reported in EAGLE-I, taken after readings that hold more than one collection snapshot are replaced (see flagged_readings). A replaced reading is an interpolated value that was not measured | No utility record for the county in the window. peak_reason is set and reason says why |
| `peak_reason` | string |  | Why peak_customers_out is empty: no_utility_record. reason gives the cause (for example county_not_declared). Values: `no_utility_record` | peak_customers_out has a value |
| `peak_customers_out_raw` | number |  | Highest reading in the window as the EAGLE-I year file records it, before any filter | peak_customers_out is empty |
| `flagged_readings` | integer |  | Readings in the window that held more than one collection snapshot and were replaced. 0 when none | peak_customers_out is empty |
| `peak_share_out` | number |  | peak_customers_out divided by customers_total | No share. peak_share_reason says why |
| `peak_share_reason` | string |  | Why peak_share_out is empty. no_utility_record: no EAGLE-I rows. no_customers_total: customers_total is empty and customers_reason says why. peak_above_customer_estimate: the peak is above the customer estimate. Values: `no_customers_total`, `no_utility_record`, `peak_above_customer_estimate` | peak_share_out has a value |
| `customer_hours_out` | number | customer-hours | Customer-hours out in the window from impact_date, or up to a reporting drop when customer_hours_reason is reporting_drop | peak_customers_out is empty |
| `hours_to_50pct_restored` | number | hours | Hours from the peak until customers out stayed at or below 50% of the peak for 6 hours | Not measured. hours_to_50pct_reason says why |
| `hours_to_50pct_reason` | string |  | Why hours_to_50pct_restored is empty. not_restored_in_window: still above half the peak at the end. no_customers_out: the peak is 0. no_utility_record: no EAGLE-I rows. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `not_restored_in_window`, `no_customers_out`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_to_50pct_restored has a value |
| `hours_to_90pct_restored` | number | hours | Hours from the peak until customers out stayed at or below 10% of the peak for 6 hours | Not measured. hours_to_90pct_reason says why |
| `hours_to_90pct_reason` | string |  | Why hours_to_90pct_restored is empty. not_restored_in_window: still above 10% of the peak at the end. no_customers_out: the peak is 0. no_utility_record: no EAGLE-I rows. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `not_restored_in_window`, `no_customers_out`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_to_90pct_restored has a value |
| `hours_under_1pct_customers` | number | hours | Hours from the peak until customers out stayed at or below 1% of customers_total for 6 hours | Not measured. hours_under_1pct_reason says why |
| `hours_under_1pct_reason` | string |  | Why hours_under_1pct_customers is empty. never_above_1pct: the outage never passed 1% of customers. not_under_1pct_in_window: still above 1% at the end. no_customers_total, peak_above_customer_estimate or no_utility_record: nothing to measure against. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `never_above_1pct`, `not_under_1pct_in_window`, `no_customers_total`, `peak_above_customer_estimate`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_under_1pct_customers has a value |
| `coverage_gap` | boolean |  | True when the utility series has a gap longer than 6 hours after the peak | peak_customers_out is empty |
| `customers_total` | number | customers | Estimated electric customers in the county: the state's EIA-861 customer count split across counties by Census housing units | No estimate. customers_reason says why |
| `customers_reason` | string |  | Why customers_total is empty. eia861_territory_incomplete, no_housing_units: the estimate could not be made for this county. outage_exceeds_*: the peak, after flagged readings are replaced, is above the estimate. The peak is published as reported, and the suffix says which other customer counts it also exceeds. Values: `eia861_territory_incomplete`, `no_housing_units`, `outage_exceeds_customer_estimate`, `outage_exceeds_estimate_and_mcc`, `outage_exceeds_estimate_and_eaglei_total`, `outage_exceeds_every_customer_model` | customers_total has a value |
| `estimate_exceeded_in_other_storm` | boolean |  | True when this county's peak was above its customer estimate in another storm of the catalog. The share here then rests on an estimate that may be too low | Never empty |
| `outage_window_end_day` | integer | days | Last day of the outage window, counted from impact_date: 45, or earlier at the next FEMA storm in the county | Never empty |
| `outage_window_end_reason` | string |  | window: the full 45 days. next_storm:DR-number: the next FEMA storm in the county | Never empty |
| `window_note` | string |  | window_cut_at_source_end: the 45-day outage window runs past 31 December 2025, the last day of the published EAGLE-I record, so records stop there. Values: `window_cut_at_source_end` | The outage window is not cut, or the storm has no outage run |
| `customers_source` | string |  | EIA-861 customer table and year used for customers_total | Never empty |
| `customer_hours_reason` | string |  | reporting_drop: the integral stops at a one-step collapse of the utility feed. The tail of the window is not counted. Values: `reporting_drop` | The integral covers the window, or peak_customers_out is empty |
| `reporting_drop` | boolean |  | True when a restore hour is empty because the utility feed fell in one 15-minute step and did not come back. The answer to give is: The utility's outage feed stopped reporting for this county partway through, so a restoration time cannot be given. | peak_customers_out is empty |

## `declared_unmatched.csv`

Declared counties with no row in the boundary file, kept with a reason. Key: `event_id`, `geoid`.
Every row joins `storms` on `event_id`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `geoid` | string |  | County FIPS code, 5 digits. Read as text to keep the leading zero | Never empty |
| `declared_via` | string |  | The declaration that names the county. Values: `major_disaster`, `emergency` | Never empty |
| `reason` | string |  | merged_county_not_in_boundaries: the county was merged into another and the boundary file no longer has it. not_in_boundaries: no such county in the boundary file. outside_storm_states: in the boundary file, but its state is not in the storm's states. Values: `merged_county_not_in_boundaries`, `not_in_boundaries`, `outside_storm_states` | Never empty |
| `note` | string |  | What happened to the county | Never empty |

## `tribal_area_summary.csv`

One row per tribal declaration storm and tribal area, the area FEMA named. Key: `event_id`, `region_id`.
Every row joins `storms` on `event_id`, and holds the same `product`.
One product per storm: `product` is one value within each `event_id`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `region_scheme` | string |  | Boundary set of the area: us-aiannh-2024, the Census 2024 American Indian, Alaska Native and Native Hawaiian areas file. Values: `us-aiannh-2024` | Never empty |
| `region_id` | string |  | Census area code, 4 digits. Read as text to keep the leading zero | Never empty |
| `region_name` | string |  | Census area name | Never empty |
| `state` | string |  | State postal code of the declaration | Never empty |
| `region_role` | string |  | tribal_area: the row describes the tribal area FEMA named. Values: `tribal_area` | Never empty |
| `declared_via` | string |  | major_disaster: FEMA filed tribal declarations as major disasters. Values: `major_disaster` | Never empty |
| `thin_region` | boolean |  | True when the area has fewer than 20 pixels on its tiles. Its numbers are kept and are noisy | Never empty |
| `product` | string |  | Night-light product the storm is measured with: VNP46A2 (Suomi NPP) or VJ146A2 (NOAA-20). One product per storm. Radiance from different products should not be compared between storms. Values: `VNP46A2`, `VJ146A2` | Never empty |
| `baseline_radiance` | number | nW/cm²/sr | Median radiance of the clear baseline nights before the storm | baseline_source is insufficient: there were no baseline nights |
| `baseline_nights` | integer |  | Clear nights in the baseline | Never empty |
| `baseline_source` | string |  | event_window: baseline nights before the storm. prior_year: the same season a year earlier, used when the nights before the storm were too few. insufficient: no baseline. Values: `event_window`, `prior_year`, `insufficient` | Never empty |
| `post_obs_nights` | integer |  | Nights with usable pixels after the landfall date | Never empty |
| `median_valid_pixel_share` | number |  | Median share of usable pixels after the landfall date | Never empty |
| `status` | string |  | What the night-light series did. It is not a detected power outage. light_drop: smoothed light fell below the county's normal range soon after impact. no_measurable_outage: observed, no such fall (the name keeps an old use of the word outage for a night-light state). cloud_obscured: not observed until late and normal by then. low_signal: too noisy to judge. insufficient_data: too few nights. Values: `light_drop`, `no_measurable_outage`, `cloud_obscured`, `low_signal`, `insufficient_data` | Never empty |
| `outage_min_ratio` | number |  | Lowest smoothed light ratio after impact (a night-light value despite the name) | status is low_signal or insufficient_data |
| `outage_min_day` | integer | days | Day of that lowest ratio, counted from impact_date | status is low_signal or insufficient_data |
| `days_to_50` | integer | days | Days from impact until smoothed light was back at or above 50% of baseline | Not measured. days_to_50_reason says why |
| `days_to_50_reason` | string |  | Why days_to_50 is empty. never_below_50: a light_drop status, but light never fell below 50%. not_back_to_50_in_window: fell below 50% and did not return. no_outage_measured: observed, no light drop found (a night-light state despite the name). not_observed_cloud, not_observed_too_few_nights: the county was not observed. not_measurable_low_signal: its light is too noisy to judge. Values: `never_below_50`, `not_back_to_50_in_window`, `no_outage_measured`, `not_observed_cloud`, `not_observed_too_few_nights`, `not_measurable_low_signal` | days_to_50 has a value |
| `days_to_normal` | integer | days | Days from impact until smoothed light was back in the county's normal range | Not measured. days_to_normal_reason says why |
| `days_to_normal_reason` | string |  | Why days_to_normal is empty. not_back_to_normal_in_window: a light_drop status that did not return to normal. The other codes are as in days_to_50_reason. Values: `not_back_to_normal_in_window`, `no_outage_measured`, `not_observed_cloud`, `not_observed_too_few_nights`, `not_measurable_low_signal` | days_to_normal has a value |
| `recovery_uncertain` | boolean |  | True when a gap of 5 or more days without a clear night comes just before days_to_normal | days_to_normal is empty |
| `window_end_day` | integer | days | Last day of the night-light window, counted from impact_date | Never empty |
| `window_end_reason` | string |  | window: the full window. data_end: the stored nights stop earlier. next_storm:DR-number: the next FEMA storm in the county | Never empty |
| `impact_date` | date |  | Date the storm reached the county, day 0 of the window | Never empty |
| `impact_source` | string |  | How impact_date was chosen. track_within_250km: first UTC date the HURDAT2 track came within 250 km of the county. track_closest_approach: the track never came that close, so the date of closest approach. catalog_landfall: storms.landfall. Values: `track_within_250km`, `track_closest_approach`, `catalog_landfall` | Never empty |
| `clear_nights_pre` | integer |  | Clear nights before impact | Never empty |
| `clear_nights_post` | integer |  | Clear nights after impact | Never empty |
| `method_version` | string |  | Night-light method version. Values: `v3` | Never empty |
| `source_night_light` | string |  | Layer marker. Values: `night_light` | Never empty |
| `post_days_window` | integer | days | Days after the landfall date covered by stored nights | Never empty |
| `outage_reason` | string |  | no_county_outage_record: EAGLE-I reports counties, so there is no outage record for a tribal area. Values: `no_county_outage_record` | Never empty |
| `peak_customers_out` | number |  | Peak customers out. No source reports it for a tribal area | Always. outage_reason says why |
| `customer_hours_out` | number | customer-hours | Customer-hours out. No source reports it for a tribal area | Always. outage_reason says why |
| `customers_total` | number | customers | Electric customers in the area. EIA-861 counts are by county | Always. customers_reason says why |
| `customers_reason` | string |  | no_county_customer_count: EIA-861 customer counts are by county. Values: `no_county_customer_count` | Never empty |
| `peak_share_out` | number |  | Share of customers out at the peak | Always. peak_share_reason says why |
| `peak_share_reason` | string |  | no_county_customer_count: there is no customer count for the area. Values: `no_county_customer_count` | Never empty |

## `tribal_area_daily.csv`

One row per tribal declaration storm, tribal area and night. Key: `event_id`, `region_id`, `date`.
Every row joins `tribal_area_summary` on `event_id`, `region_id`, and holds the same `region_scheme`, `declared_via`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `region_scheme` | string |  | Boundary set of the area: us-aiannh-2024, the Census 2024 American Indian, Alaska Native and Native Hawaiian areas file. Values: `us-aiannh-2024` | Never empty |
| `region_id` | string |  | Census area code, 4 digits. Read as text to keep the leading zero | Never empty |
| `date` | date |  | Night of observation (the UTC date of the product file) | Never empty |
| `declared_via` | string |  | major_disaster, as in tribal_area_summary. Values: `major_disaster` | Never empty |
| `days_from_landfall` | integer | days | Days since storms.landfall (negative before). Stored nights reach back about 400 days where a prior-year baseline was read | Never empty |
| `radiance_nw_cm2_sr` | number | nW/cm²/sr | Mean radiance over the valid pixels that night: the sum of radiance over valid pixels divided by their number | valid_pixels is 0. A night with no valid pixel is never written as 0 |
| `valid_pixels` | integer | pixels | Valid pixels that night: a value, Mandatory_Quality_Flag 0, confident clear and no snow | Never empty |
| `valid_pixel_share` | number |  | valid_pixels as a share of all pixels in the area | Never empty |
| `snow_excluded_share` | number |  | Snow pixels as a share of pixels with a finite radiance. A different base from valid_pixel_share, so the two can add to more than 1 | Never empty |
| `light_ratio` | number |  | radiance_nw_cm2_sr divided by baseline_radiance of the summary row | radiance_nw_cm2_sr is empty, or the summary row has no baseline |
| `thin_night` | boolean |  | True when the night has 1 to 19 valid pixels. The radiance is kept as measured and is noisy | Never empty |

## `tribal_area_counties.csv`

The counties each tribal area overlaps, with the overlap as a share of each. Slivers are left out. Key: `area_id`, `county_geoid`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `area_id` | string |  | Census area code, as region_id | Never empty |
| `area_name` | string |  | Census area name | Never empty |
| `county_geoid` | string |  | County FIPS code, 5 digits | Never empty |
| `county_name` | string |  | County name | Never empty |
| `county_namelsad` | string |  | County name with its legal description (for example Coconino County) | Never empty |
| `state_fips` | string |  | State FIPS code, 2 digits | Never empty |
| `overlap_km2` | number | km² | Area of the overlap | Never empty |
| `overlap_share_of_county` | number |  | Overlap as a share of the county's area: how much of the county lies inside the tribal area | Never empty |
| `overlap_share_of_tribal_area` | number |  | Overlap as a share of the tribal area's area | Never empty |

## `tribal_context_county_summary.csv`

Night-light summary of each county a tribal area overlaps, for the tribal declaration storms. Context rows for the whole county. Key: `event_id`, `context_for_region_id`, `geoid`.
Every row joins `tribal_area_summary` on `event_id` = `event_id`, `context_for_region_id` = `region_id`, and holds the same `product`.
Every row joins `tribal_area_counties` on `context_for_region_id` = `area_id`, `geoid` = `county_geoid`, and holds the same `overlap_share_of_county`, `overlap_share_of_tribal_area`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `context_for_region_id` | string |  | region_id of the tribal area the county row is context for | Never empty |
| `geoid` | string |  | County FIPS code, 5 digits. Read as text to keep the leading zero | Never empty |
| `region_role` | string |  | county_context: the row describes the whole county, as context for the tribal area. Values: `county_context` | Never empty |
| `overlap_share_of_county` | number |  | Overlap as a share of the county's area: how much of the county lies inside the tribal area | Never empty |
| `overlap_share_of_tribal_area` | number |  | Overlap as a share of the tribal area's area | Never empty |
| `county` | string |  | County name | Never empty |
| `state` | string |  | State or territory postal code | Never empty |
| `in_nhc_wind_radius` | boolean |  | As in county_summary | No wind radius is on file for these storms |
| `product` | string |  | Night-light product the storm is measured with: VNP46A2 (Suomi NPP) or VJ146A2 (NOAA-20). One product per storm. Radiance from different products should not be compared between storms. Values: `VNP46A2`, `VJ146A2` | Never empty |
| `baseline_radiance` | number | nW/cm²/sr | Median radiance of the clear baseline nights before the storm | baseline_source is insufficient: there were no baseline nights |
| `baseline_nights` | integer |  | Clear nights in the baseline | Never empty |
| `baseline_source` | string |  | event_window: baseline nights before the storm. prior_year: the same season a year earlier, used when the nights before the storm were too few. insufficient: no baseline. Values: `event_window`, `prior_year`, `insufficient` | Never empty |
| `post_obs_nights` | integer |  | Nights with usable pixels after the landfall date | Never empty |
| `median_valid_pixel_share` | number |  | Median share of usable pixels after the landfall date | Never empty |
| `status` | string |  | What the night-light series did. It is not a detected power outage. light_drop: smoothed light fell below the county's normal range soon after impact. no_measurable_outage: observed, no such fall (the name keeps an old use of the word outage for a night-light state). cloud_obscured: not observed until late and normal by then. low_signal: too noisy to judge. insufficient_data: too few nights. Values: `light_drop`, `no_measurable_outage`, `cloud_obscured`, `low_signal`, `insufficient_data` | Never empty |
| `outage_min_ratio` | number |  | Lowest smoothed light ratio after impact (a night-light value despite the name) | status is low_signal or insufficient_data |
| `outage_min_day` | integer | days | Day of that lowest ratio, counted from impact_date | status is low_signal or insufficient_data |
| `days_to_50` | integer | days | Days from impact until smoothed light was back at or above 50% of baseline | Not measured. days_to_50_reason says why |
| `days_to_50_reason` | string |  | Why days_to_50 is empty. never_below_50: a light_drop status, but light never fell below 50%. not_back_to_50_in_window: fell below 50% and did not return. no_outage_measured: observed, no light drop found (a night-light state despite the name). not_observed_cloud, not_observed_too_few_nights: the county was not observed. not_measurable_low_signal: its light is too noisy to judge. Values: `never_below_50`, `not_back_to_50_in_window`, `no_outage_measured`, `not_observed_cloud`, `not_observed_too_few_nights`, `not_measurable_low_signal` | days_to_50 has a value |
| `days_to_normal` | integer | days | Days from impact until smoothed light was back in the county's normal range | Not measured. days_to_normal_reason says why |
| `days_to_normal_reason` | string |  | Why days_to_normal is empty. not_back_to_normal_in_window: a light_drop status that did not return to normal. The other codes are as in days_to_50_reason. Values: `not_back_to_normal_in_window`, `no_outage_measured`, `not_observed_cloud`, `not_observed_too_few_nights`, `not_measurable_low_signal` | days_to_normal has a value |
| `recovery_uncertain` | boolean |  | True when a gap of 5 or more days without a clear night comes just before days_to_normal | days_to_normal is empty |
| `window_end_day` | integer | days | Last day of the night-light window, counted from impact_date | Never empty |
| `window_end_reason` | string |  | window: the full window. data_end: the stored nights stop earlier. next_storm:DR-number: the next FEMA storm in the county | Never empty |
| `impact_date` | date |  | Date the storm reached the county, day 0 of the window | Never empty |
| `impact_source` | string |  | How impact_date was chosen. track_within_250km: first UTC date the HURDAT2 track came within 250 km of the county. track_closest_approach: the track never came that close, so the date of closest approach. catalog_landfall: storms.landfall. Values: `track_within_250km`, `track_closest_approach`, `catalog_landfall` | Never empty |
| `clear_nights_pre` | integer |  | Clear nights before impact | Never empty |
| `clear_nights_post` | integer |  | Clear nights after impact | Never empty |
| `method_version` | string |  | Night-light method version. Values: `v3` | Never empty |
| `source_night_light` | string |  | Layer marker. Values: `night_light` | Never empty |
| `post_days_window` | integer | days | Days after the landfall date covered by stored nights | Never empty |

## `tribal_context_county_daily.csv`

One row per tribal declaration storm, overlapping county and night. Context rows for the whole county. Key: `event_id`, `context_for_region_id`, `geoid`, `date`.
Every row joins `tribal_context_county_summary` on `event_id`, `context_for_region_id`, `geoid`, and holds the same `region_role`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `context_for_region_id` | string |  | region_id of the tribal area the county row is context for | Never empty |
| `geoid` | string |  | County FIPS code, 5 digits. Read as text to keep the leading zero | Never empty |
| `region_role` | string |  | county_context: the row describes the whole county, as context for the tribal area. Values: `county_context` | Never empty |
| `date` | date |  | Night of observation (the UTC date of the product file) | Never empty |
| `days_from_landfall` | integer | days | Days since storms.landfall (negative before). Stored nights reach back about 400 days where a prior-year baseline was read | Never empty |
| `radiance_nw_cm2_sr` | number | nW/cm²/sr | Mean radiance over the valid pixels that night: the sum of radiance over valid pixels divided by their number | valid_pixels is 0. A night with no valid pixel is never written as 0 |
| `valid_pixels` | integer | pixels | Valid pixels that night: a value, Mandatory_Quality_Flag 0, confident clear and no snow | Never empty |
| `valid_pixel_share` | number |  | valid_pixels as a share of all pixels in the area | Never empty |
| `snow_excluded_share` | number |  | Snow pixels as a share of pixels with a finite radiance. A different base from valid_pixel_share, so the two can add to more than 1 | Never empty |
| `light_ratio` | number |  | radiance_nw_cm2_sr divided by baseline_radiance of the summary row | radiance_nw_cm2_sr is empty, or the summary row has no baseline |
| `thin_night` | boolean |  | True when the night has 1 to 19 valid pixels. The radiance is kept as measured and is noisy | Never empty |

## `tribal_context_utility_by_county.csv`

Outage columns of each county a tribal area overlaps, for the tribal declaration storms. Context rows for the whole county. Key: `event_id`, `context_for_region_id`, `geoid`.
Every row joins `tribal_context_county_summary` on `event_id`, `context_for_region_id`, `geoid`, and holds the same `region_role`, `overlap_share_of_county`, `overlap_share_of_tribal_area`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `context_for_region_id` | string |  | region_id of the tribal area the county row is context for | Never empty |
| `geoid` | string |  | County FIPS code, 5 digits. Read as text to keep the leading zero | Never empty |
| `region_role` | string |  | county_context: the row describes the whole county, as context for the tribal area. Values: `county_context` | Never empty |
| `overlap_share_of_county` | number |  | Overlap as a share of the county's area: how much of the county lies inside the tribal area | Never empty |
| `overlap_share_of_tribal_area` | number |  | Overlap as a share of the tribal area's area | Never empty |
| `state` | string |  | State or territory postal code | Never empty |
| `available` | boolean |  | True when utility records cover this county's window | Never empty |
| `reason` | string |  | Utility availability, as in utility_by_county. Values: `ok`, `no_rows_in_window`, `no_utility_record` | Never empty |
| `source` | string |  | utility_records when the county has EAGLE-I rows in the window, otherwise none. Values: `utility_records`, `none` | Never empty |
| `peak_customers_out` | number |  | Peak customers out reported in EAGLE-I, taken after readings that hold more than one collection snapshot are replaced (see flagged_readings). A replaced reading is an interpolated value that was not measured | No utility record for the county in the window. peak_reason is set and reason says why |
| `peak_reason` | string |  | Why peak_customers_out is empty: no_utility_record. reason gives the cause (for example county_not_declared). Values: `no_utility_record` | peak_customers_out has a value |
| `peak_customers_out_raw` | number |  | Highest reading in the window as the EAGLE-I year file records it, before any filter | peak_customers_out is empty |
| `flagged_readings` | integer |  | Readings in the window that held more than one collection snapshot and were replaced. 0 when none | peak_customers_out is empty |
| `peak_share_out` | number |  | peak_customers_out divided by customers_total | No share. peak_share_reason says why |
| `peak_share_reason` | string |  | Why peak_share_out is empty. no_utility_record: no EAGLE-I rows. no_customers_total: customers_total is empty and customers_reason says why. peak_above_customer_estimate: the peak is above the customer estimate. Values: `no_customers_total`, `no_utility_record`, `peak_above_customer_estimate` | peak_share_out has a value |
| `customer_hours_out` | number | customer-hours | Customer-hours out in the window from impact_date, or up to a reporting drop when customer_hours_reason is reporting_drop | peak_customers_out is empty |
| `hours_to_50pct_restored` | number | hours | Hours from the peak until customers out stayed at or below 50% of the peak for 6 hours | Not measured. hours_to_50pct_reason says why |
| `hours_to_50pct_reason` | string |  | Why hours_to_50pct_restored is empty. not_restored_in_window: still above half the peak at the end. no_customers_out: the peak is 0. no_utility_record: no EAGLE-I rows. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `not_restored_in_window`, `no_customers_out`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_to_50pct_restored has a value |
| `hours_to_90pct_restored` | number | hours | Hours from the peak until customers out stayed at or below 10% of the peak for 6 hours | Not measured. hours_to_90pct_reason says why |
| `hours_to_90pct_reason` | string |  | Why hours_to_90pct_restored is empty. not_restored_in_window: still above 10% of the peak at the end. no_customers_out: the peak is 0. no_utility_record: no EAGLE-I rows. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `not_restored_in_window`, `no_customers_out`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_to_90pct_restored has a value |
| `hours_under_1pct_customers` | number | hours | Hours from the peak until customers out stayed at or below 1% of customers_total for 6 hours | Not measured. hours_under_1pct_reason says why |
| `hours_under_1pct_reason` | string |  | Why hours_under_1pct_customers is empty. never_above_1pct: the outage never passed 1% of customers. not_under_1pct_in_window: still above 1% at the end. no_customers_total, peak_above_customer_estimate or no_utility_record: nothing to measure against. reporting_drop: a one-step collapse of the feed is what crossed the threshold. peak_mismatch: the 15-minute series does not reproduce the published peak. Values: `never_above_1pct`, `not_under_1pct_in_window`, `no_customers_total`, `peak_above_customer_estimate`, `no_utility_record`, `reporting_drop`, `peak_mismatch` | hours_under_1pct_customers has a value |
| `coverage_gap` | boolean |  | True when the utility series has a gap longer than 6 hours after the peak | peak_customers_out is empty |
| `customers_total` | number | customers | Estimated electric customers in the county: the state's EIA-861 customer count split across counties by Census housing units | No estimate. customers_reason says why |
| `customers_reason` | string |  | Why customers_total is empty, as in utility_by_county. Values: `eia861_territory_incomplete`, `no_housing_units`, `outage_exceeds_customer_estimate`, `outage_exceeds_estimate_and_mcc`, `outage_exceeds_estimate_and_eaglei_total`, `outage_exceeds_every_customer_model` | customers_total has a value |
| `estimate_exceeded_in_other_storm` | boolean |  | True when this county's peak was above its customer estimate in another storm of the catalog. The share here then rests on an estimate that may be too low | Never empty |
| `outage_window_end_day` | integer | days | Last day of the outage window, counted from impact_date: 45, or earlier at the next FEMA storm in the county | Never empty |
| `outage_window_end_reason` | string |  | window: the full 45 days. next_storm:DR-number: the next FEMA storm in the county | Never empty |
| `customers_source` | string |  | EIA-861 customer table and year used for customers_total | Never empty |
| `customer_hours_reason` | string |  | reporting_drop: the integral stops at a one-step collapse of the utility feed. The tail of the window is not counted. Values: `reporting_drop` | The integral covers the window, or peak_customers_out is empty |
| `reporting_drop` | boolean |  | True when a restore hour is empty because the utility feed fell in one 15-minute step and did not come back. The answer to give is: The utility's outage feed stopped reporting for this county partway through, so a restoration time cannot be given. | peak_customers_out is empty |

## `validation.csv`

Night light against reported outages, one row per storm and night-light measure, for the storms with an outage run. Key: `event_id`, `measure`.
Every row joins `storms` on `event_id`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `event_id` | string |  | NHC storm identifier (for example AL092022) or FEMA disaster number (DR-4901) | Never empty |
| `measure` | string |  | Night-light measure scored: dark_county_mean, dark_lit_ratio or dark_lit_share. Values: `dark_county_mean`, `dark_lit_ratio`, `dark_lit_share` | Never empty |
| `n_high` | integer |  | Declared counties with 10% or more of customers out at the peak and a value of the measure | Never empty |
| `n_low` | integer |  | Declared counties with under 1% of customers out at the peak and a value of the measure | Never empty |
| `auc` | number |  | Chance that a high-outage county is darker than a low-outage county on the measure. 0.5 is chance | Not scored. reason says why |
| `se_hanley_mcneil` | number |  | Standard error of auc (Hanley-McNeil) | auc is empty |
| `ci_low` | number |  | Lower end of the 95% interval for auc | auc is empty |
| `ci_high` | number |  | Upper end of the 95% interval for auc | auc is empty |
| `p_unadjusted` | number |  | Two-sided p-value of the Mann-Whitney test between high-outage and low-outage counties, so a reversed storm can count | auc is empty |
| `p_holm` | number |  | p_unadjusted after the Holm step-down correction over the scored storms of the measure | auc is empty |
| `reason` | string |  | Why auc is empty: fewer than 3 high counties, fewer than 3 low counties, or both. Values: `fewer_than_3_high`, `fewer_than_3_low`, `fewer_than_3_high_and_low` | auc has a value |
| `product` | string |  | Night-light product the storm is measured with: VNP46A2 (Suomi NPP) or VJ146A2 (NOAA-20). One product per storm. Radiance from different products should not be compared between storms. Values: `VNP46A2`, `VJ146A2` | Never empty |
| `state_group` | string |  | The states joined to the storm's states through storms they share, space-separated. Storms with the same state_group sit in the same holdout fold | Never empty |

## `validation_pooled.csv`

Night light against reported outages pooled over storms, one row per measure and scope. Key: `measure`, `scope`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `measure` | string |  | Night-light measure scored. Values: `dark_county_mean`, `dark_lit_ratio`, `dark_lit_share` | Never empty |
| `scope` | string |  | Storms pooled: all, product:<product>, kind:tropical_cyclone, kind:other, or year:<landfall year> | Never empty |
| `n_storms` | integer |  | Storms with at least one scored county in the scope | Never empty |
| `n_counties` | integer |  | Storm-county rows scored, high and low together | Never empty |
| `auc` | number |  | Pooled chance that a high-outage county is darker than a low-outage county. 0.5 is chance | Too few high or low counties in the scope |
| `ci_hm_low` | number |  | Lower end of the Hanley-McNeil 95% interval, counties treated as independent | auc is empty |
| `ci_hm_high` | number |  | Upper end of the Hanley-McNeil 95% interval | auc is empty |
| `ci_boot_low` | number |  | Lower end of the 95% interval from resampling whole storms. The headline uses this interval | auc is empty |
| `ci_boot_high` | number |  | Upper end of the 95% interval from resampling whole storms | auc is empty |

## `validation_holdout.csv`

Pooled AUC on each fold of a grouped holdout that keeps whole groups of states together. Key: `fold`, `measure`.

| Column | Type | Unit | Meaning | When empty |
|---|---|---|---|---|
| `fold` | integer |  | Fold number | Never empty |
| `states` | string |  | States in the fold, space-separated | Never empty |
| `n_storms` | integer |  | Storms in the fold | Never empty |
| `measure` | string |  | Night-light measure scored. Values: `dark_county_mean`, `dark_lit_ratio`, `dark_lit_share` | Never empty |
| `auc` | number |  | Pooled AUC over the fold's storms. 0.5 is chance | Never empty |

