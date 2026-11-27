# Data Quality Report

| Check | Result | Action |
|---|---|---|
| Rows / columns | 1,338 x 7 | - |
| Missing values | 0 in every column | None needed |
| Exact duplicate rows | 1 pair (age 19, male, BMI 30.59, 0 children, non-smoker, northwest, charges 1,639.5631) | Kept first, removed second (0.01 % of total charges). No ID column exists, so a true double entry cannot be proven; identical charges to 4 decimals make coincidence very unlikely |
| Data types | All appropriate; categoricals cast to category | - |
| Categorical consistency | sex, smoker, region have clean, consistent labels (no casing or spelling variants) | Lower-cased/trimmed defensively |
| Range plausibility | age 18-64; BMI 15.96-53.13; children 0-5; charges all > 0 | Retained |
| Outliers | 139 charges above the dataset-wide IQR fence (34,524.78); skewness of charges = 1.52 | Retained and flagged, since extreme charges are plausible for high-risk members and are the subject of the analysis |
| Coverage limits | No dates, providers, patient IDs, diagnoses | Related analyses omitted rather than invented |
| Privacy | No names, contact data or direct identifiers in the file | `record_id` is a row number only |
