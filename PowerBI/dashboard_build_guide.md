# Power BI Build Guide (Power BI Desktop)

Power BI `.pbix` files can only be authored in Power BI Desktop, so this guide, `power_query.m`, `DAX_measures.dax`
and `theme.json` give you everything needed to assemble the report in roughly 60-90 minutes.

## 0. Scope adaptation (read first)

The brief asked for monthly trends, provider analysis, medical condition, admission type and unique patients.
The supplied dataset has **no** date, provider, diagnosis, admission type or patient ID, so those visuals are not built.
Each page below keeps the requested *purpose* using only fields that exist.

| Requested item | Status | What the dashboard uses instead |
|---|---|---|
| Monthly claims trend | Not possible (no date) | Charge-band distribution and average charge by age group |
| Unique patients | Not possible (no patient ID) | Total Records (one row = one beneficiary record) |
| Claims by medical condition / admission type | Not possible | Smoker status, BMI category, number of children (risk factors, **not** diagnoses) |
| Insurance provider analysis | Not possible (no provider) | Region comparison (only organisational/geographic field) |
| Fraud | Cannot be assessed | Peer-relative anomaly flags labelled "for review" |

## 1. Load data

1. Open Power BI Desktop. **Home > Get data > Text/CSV**, choose `Dataset/processed/claims_clean.csv`, click **Transform Data**.
2. Open **Advanced Editor** and replace the query with `PowerBI/power_query.m` (edit the file path). Name the query `claims`. **Close & Apply**.
3. (Optional) Also import `summary_*.csv`, `statistical_tests.csv`, `log_linear_model.csv` for reference tables. They are not required by the measures.

## 2. Model

* Single table `claims` (no relationships needed).
* **Sort by column:** `age_group` by `age_group_order`; `bmi_category` by `bmi_category_order`; `charge_band` by `charge_band_order`.
* Hide helper columns: `*_order`, `log_charges`, `smoker_flag`, `peer_upper_fence`.
* Formats: `charges` Currency (or Decimal, 2dp; the dataset does not state a currency); `% ` measures as Percentage 1dp.
* Create a blank table `_Measures` and paste every measure from `DAX_measures.dax` (sections 1-7). Skip sections 8-9 (documentation only).

## 3. Theme and canvas

**View > Themes > Browse for themes** > `PowerBI/theme.json`. Canvas 16:9 (1280x720). Left-align a title band at the top of each page.
Add a footer text box on every page: `Source: insurance.csv | 1,337 records after removing 1 exact duplicate | No dates, providers or patient IDs available`.

## 4. Pages

Global slicers (sync across pages via **View > Sync slicers**): `sex`, `region`, `smoker_label`, `age_group`.

### Page 1 - Executive Overview
| Visual | Fields |
|---|---|
| Card x6 | `Total Records`, `Total Charges`, `Average Charge`, `Median Charge`, `Highest Charge`, `High-Cost Share of Charges %` |
| Clustered bar | Axis `smoker_label`; Values `% of Total Records`, `% of Total Charges` |
| Column | Axis `age_group`; Values `Average Charge` |
| Column (distribution) | Axis `charge_band`; Values `Total Records` |
| Text card | `Executive Insight` measure |

### Page 2 - Patient & Medical Profile
| Visual | Fields |
|---|---|
| Combo (column + line) | Axis `age_group`; Column `Total Records`; Line `Average Charge` |
| Bar | Axis `sex`; Values `Average Charge` and `Total Records` |
| Clustered column | Axis `bmi_category`; Values `Average Charge`; Legend `smoker_label` |
| Column | Axis `children`; Values `Average Charge` (note small n at 4-5 children: 25 and 18 records) |
| Matrix heatmap | Rows `smoker_label`; Columns `bmi_category`; Values `Average Charge`; Conditional formatting > Background colour scale |
| Scatter | X `age`; Y `charges`; Legend `smoker_label` |

### Page 3 - Regional Analysis (provider substitute)
| Visual | Fields |
|---|---|
| Column | Axis `region`; Values `Total Records` |
| Column | Axis `region`; Values `Average Charge` |
| Column | Axis `region`; Values `Total Charges` |
| 100 % stacked column | Axis `region`; Legend `smoker_label`; Values `Total Records` (shows composition behind regional differences) |
| Table | `region`, `Total Records`, `Total Charges`, `Average Charge`, `% of Total Charges`, `High-Cost Rate %`, `Region Rank (by Average Charge)` |
| Column | Axis `region`; Values `High-Cost Rate %` |

Add a text box: *"Region is the only grouping available. It is not an insurance provider."*

### Page 4 - Claims Risk & Cost
| Visual | Fields |
|---|---|
| Card x4 | `High-Cost Threshold (P90)`, `High-Cost Records`, `Peer Anomaly Records`, `Peer Anomaly Share of Charges %` |
| Column (histogram) | Axis `charge_band`; Values `Total Records` and `% of Total Charges` |
| Scatter | X `age`; Y `charges`; Legend `is_peer_anomaly` (anomalies in red) |
| Bar | Axis `smoker_bmi_segment`; Values `% of Total Charges` and `% of Total Records` |
| Table (top 15) | `record_id`, `age`, `sex`, `bmi`, `smoker_label`, `region`, `charges`, `charge_vs_peer_median`; filter `is_peer_anomaly = TRUE`; sort by `charge_vs_peer_median` desc |
| Text box | Definitions: *High-cost = above P90. Peer anomaly = above Tukey fence within smoker x age-group peers. Both are review flags, **not** fraud indicators.* |

Power BI has no native box plot. Use the Python figure `Screenshots/python_eda/05_smoker_boxplot.png` as an image, or the AppSource "Box and Whisker" visual.

## 5. Validate before publishing

Clear all slicers and confirm the cards match these values (computed independently in Python and SQL):

| Measure | Expected |
|---|---|
| Total Records | 1,337 |
| Total Charges | 17,754,185.43 |
| Average Charge | 13,279.12 |
| Median Charge | 9,386.16 |
| Highest Charge | 63,770.43 |
| High-Cost Threshold (P90) | 34,832.74 |
| High-Cost Records | 134 |
| Peer Anomaly Records | 105 |
| Smoker Cost Multiple | 3.80 |

## 6. Steps that MUST be done manually in Power BI Desktop

1. Point the Power Query `Source` path to your local `claims_clean.csv`.
2. Apply `theme.json`.
3. Create the `_Measures` table and paste the DAX.
4. Set "Sort by column" for `age_group`, `bmi_category`, `charge_band`.
5. Build the four pages (tables above), format visuals, and set up synced slicers.
6. Run the validation table in section 5.
7. Save as `PowerBI/Healthcare_Claims_Dashboard.pbix`; export each page to PNG into `Screenshots/powerbi_dashboard/`.
8. (Optional) Publish to Power BI Service. The dataset is anonymous and contains no personal identifiers, but check your own data-sharing policy first.
