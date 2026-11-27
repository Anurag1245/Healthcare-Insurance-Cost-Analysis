# Methodology

1. **Load and validate** (`data_loader.py`): schema must match the 7 expected columns.
2. **Quality report and cleaning** (`cleaning.py`): standardise text, remove exact duplicates, add analytical columns.
3. **KPIs and group summaries** (`analysis.py`): records, total/mean/median/max charges, share of records vs share of charges, high-cost rate per group.
4. **Correlation:** Pearson and Spearman (`smoker_flag` encoded 0/1).
5. **Hypothesis tests:** Mann-Whitney U (two groups) and Kruskal-Wallis H (3+ groups), chosen because charges are right-skewed. Effect sizes: rank-biserial |r| and epsilon-squared.
6. **Regression:** OLS on log(charges) with age, BMI, children, smoker, sex, obese, smoker x obese, region dummies (R-squared 0.788). Coefficients are converted to approximate % effects. These are **associations, not causal effects**.
7. **Three separate "unusual" definitions:**
   * High-cost: charges > P90 (a business rule).
   * Dataset-wide IQR outlier: statistical distance from the whole distribution.
   * Peer anomaly: Tukey fence inside smoker x age-group peers.
   None is evidence of fraud. Fraud requires labelled cases, provider/date/procedure detail and investigation.
8. **Exports** (`run_pipeline.py`): clean data, summaries and flagged records as CSV for Power BI; figures as PNG.
9. **Validation** (`validate_outputs.py`): 29 reconciliation checks. SQL equivalents (`sql_equivalents.sql`) were run against the exported data and match.

## Design choices
* The peer-anomaly rule was chosen over a regression-residual rule after testing both. A log-linear residual approach over-predicted costs for older smokers and flagged about 12 % of records, which made it less actionable.
* `charges` has no stated currency, so no currency symbol is used.
