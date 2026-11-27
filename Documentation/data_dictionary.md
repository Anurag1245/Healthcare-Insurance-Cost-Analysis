# Data Dictionary

## Raw file: `Dataset/insurance.csv` (1,338 rows x 7 columns)

| Column | Type | Description | Observed values |
|---|---|---|---|
| age | integer | Age of the primary beneficiary | 18-64 |
| sex | text | Sex of the beneficiary | female, male |
| bmi | float | Body-mass index | 15.96-53.13 |
| children | integer | Number of children / dependents covered | 0-5 |
| smoker | text | Smoking status | yes, no |
| region | text | US residential area (as labelled in the file) | northeast, northwest, southeast, southwest |
| charges | float | Individual medical costs billed by health insurance (currency not stated) | 1,121.87-63,770.43 |

**Not present:** patient/claim ID, dates, provider/insurer, diagnosis, procedure, admission type, claim status.
The file contains no names or direct personal identifiers.

## Engineered columns (`Dataset/processed/claims_clean.csv`)

| Column | Logic |
|---|---|
| record_id | Sequential surrogate row key (not a patient ID) |
| age_group | 18-24, 25-34, 35-44, 45-54, 55-64 |
| bmi_category | WHO adult bands: Underweight <18.5, Normal 18.5-24.9, Overweight 25-29.9, Obese >=30 |
| has_children | children > 0 |
| smoker_flag | 1 if smoker = yes |
| log_charges | natural log of charges (used for modelling) |
| charge_band | <5K, 5K-10K, 10K-20K, 20K-40K, 40K+ |
| smoker_bmi_segment | Smoker/Non-smoker x Obese/Non-obese |
| is_high_cost | charges > 90th percentile (34,832.74) |
| is_iqr_outlier | charges > Q3 + 1.5 x IQR over all records (34,524.78) |
| peer_median_charge / peer_upper_fence / charge_vs_peer_median | Median, Tukey upper fence and ratio inside the record's smoker x age-group peer set |
| is_peer_anomaly / anomaly_direction | Charges outside the peer-set Tukey fences (review flag only) |
