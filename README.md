# Healthcare Insurance Claims Analysis & Cost Optimization Dashboard

Python + Power BI portfolio project analysing what drives individual medical charges in a health-insurance dataset
and where cost is concentrated.

> **Dataset scope, stated up front.** The supplied file (`insurance.csv`) has 7 columns: `age, sex, bmi, children, smoker, region, charges`.
> It has **no** claim date, insurance provider, patient ID, diagnosis or admission type. Analyses that need those
> (monthly trends, provider comparison, condition/admission analysis, unique patients, fraud assessment) are
> **deliberately not included**; nothing was invented. See [Limitations](#limitations).

## Business problem
A health insurer needs to know who generates cost, how concentrated it is, and which segments to review for
cost-management programmes, without mistaking "expensive" for "fraudulent".

## Objectives
1. Profile charges across demographics and risk factors.
2. Quantify cost concentration (high-cost records, segments).
3. Separate *high-cost*, *statistical outlier* and *peer-relative anomaly*; none is treated as fraud.
4. Deliver a reproducible Python pipeline and a 4-page Power BI dashboard specification with DAX.

## Dataset
| Column | Meaning |
|---|---|
| age, sex, bmi, children, smoker, region | Beneficiary attributes |
| charges | Individual medical costs billed by insurance (currency not stated) |

1,338 raw rows; 1,337 after removing one exact duplicate. No direct identifiers. Full detail: [`Documentation/data_dictionary.md`](Documentation/data_dictionary.md).

## Tools
Python 3 (Pandas, NumPy, Matplotlib, Seaborn, SciPy), Jupyter, Power BI Desktop (DAX, Power Query M), SQL (cross-check).

## Repository structure
```
Healthcare-Insurance-Claims-Analysis/
├── README.md
├── requirements.txt
├── Dataset/
│   ├── insurance.csv                 raw data (unchanged)
│   └── processed/                    cleaned data, summaries, flagged records (Power BI inputs)
├── Python/
│   ├── config.py  data_loader.py  cleaning.py  analysis.py  anomaly.py  visuals.py
│   ├── run_pipeline.py               end-to-end run
│   └── validate_outputs.py           29 reconciliation checks
├── Notebooks/01_healthcare_claims_analysis.ipynb   executed notebook
├── PowerBI/  DAX_measures.dax  power_query.m  theme.json  dashboard_build_guide.md
├── Documentation/  data_dictionary.md  data_quality_report.md  methodology.md  sql_equivalents.sql
└── Screenshots/  python_eda/ (generated)   powerbi_dashboard/ (add after building the report)
```

## Data cleaning
| Issue | Result | Action |
|---|---|---|
| Missing values | 0 | none |
| Exact duplicates | 1 pair | removed the second row |
| Types / labels | consistent | categoricals cast, text trimmed |
| Outliers | 139 records above dataset-wide IQR fence (34,524.78) | kept and flagged |

Engineered columns: age group, WHO BMI category, charge band, smoker x obesity segment, high-cost flag (> P90 = 34,832.74), IQR-outlier flag, peer-anomaly flags.

## Python methodology
Modular pipeline (load > validate > clean > analyse > export). Non-parametric tests (Mann-Whitney, Kruskal-Wallis) because charges are right-skewed (skewness 1.52); OLS on log(charges) for adjusted associations; Tukey fences inside smoker x age-group peers for anomalies. Details in [`methodology.md`](Documentation/methodology.md).

## Key findings
All numbers come from `Dataset/processed/` and were reconciled by `validate_outputs.py` and SQL.

**Overall:** 1,337 records; total charges 17,754,185; average 13,279; median 9,386; highest 63,770.

1. **Smoking is the dominant cost driver.** Smokers are 20.5 % of records but 49.5 % of total charges; average 32,050 vs 8,441 for non-smokers (3.8x). Correlation with charges: 0.79 (Pearson).
2. **Cost is extremely concentrated in smokers with obesity (BMI >= 30).** 145 records (10.9 %) account for 33.9 % of charges, averaging 41,558. 127 of them (87.6 %) are in the top-10 % cost tier. Obesity alone, among non-smokers, is associated with only ~11 % higher average cost (8,856 vs 7,977), and the regression shows its cost effect is concentrated in smokers.
3. **High-cost records (top 10 %, > 34,833):** 134 records generate 32.0 % of charges; 97.8 % are smokers and 96.3 % are obese.
4. **Age raises cost steadily.** Average charge rises from 9,038 (18-24) to 18,513 (55-64); ages 45-64 are 39.6 % of records but 50.9 % of charges. Each extra year of age is associated with ~3.5 % higher charges (adjusted).
5. **Sex and region are not statistically significant** in the distribution of charges (p = 0.69 and 0.20). Raw differences mostly reflect mix: the southeast has the highest average (14,735) but also the highest smoker share (25.0 %) and obesity share (66.8 %); adjusted for these, southeast is ~14 % *lower* than northeast. Males have a higher smoker share (23.6 % vs 17.4 %).
6. **Children:** each additional child is associated with ~11 % higher charges after adjustment (small sample at 4-5 children).
7. **Regression:** R-squared 0.79 on log(charges) using only these fields.
8. **Peer anomalies:** 105 records (7.9 %; 12.4 % of charges) are unusually expensive *for their smoker x age peers*. All are non-smokers, typically ~2.9x their peer median (charges mostly 10K-37K). Only 3 overlap with the high-cost tier, so this list is complementary to, not a subset of, the high-cost list. The data contains nothing that explains them, so they are candidates for **data enrichment and clinical review**, not fraud.

## Business recommendations
These are directions for investigation; the dataset cannot estimate savings.
1. **Target smoking-cessation and weight-management programmes at smokers with obesity**: 10.9 % of members, 33.9 % of cost.
2. **Prioritise case management for the top-cost tier**; 98 % of it is smokers.
3. **Price/underwrite on smoking status and age first**; sex and region add little once these are known.
4. **Capture richer data** (claim dates, provider, diagnosis/procedure codes, patient ID). This enables trend analysis, provider benchmarking and meaningful fraud-risk screening.
5. **Review the 105 peer-anomalous non-smoker records** to learn what drives their mid-tier costs (for example chronic conditions), before any conclusion about misuse.

## KPIs and DAX
Defined in [`PowerBI/DAX_measures.dax`](PowerBI/DAX_measures.dax): Total Records, Total Charges, Average/Median/Highest Charge, High-Cost Threshold/Records/Rate/Share, % of Total Charges/Records, Smoker Cost Multiple, Region Rank, IQR Outlier and Peer Anomaly measures. Measures for unique patients, monthly growth and provider cost are documented as **not available** with templates for when such columns exist.

## Dashboard (4 pages)
1. **Executive Overview**: KPI cards, smoker cost share, average charge by age group, charge-band distribution.
2. **Patient & Medical Profile**: age, sex, BMI category, children, smoker x BMI heatmap (risk factors, not diagnoses).
3. **Regional Analysis**: region comparison (stand-in for provider analysis, which the data cannot support).
4. **Claims Risk & Cost**: high-cost tier, charge distribution, peer anomalies, cost-concentration segments.

The `.pbix` must be built in Power BI Desktop; follow [`PowerBI/dashboard_build_guide.md`](PowerBI/dashboard_build_guide.md), which lists every visual, field and expected validation value. Add screenshots to `Screenshots/powerbi_dashboard/` afterwards.

## Limitations
* No dates, provider, diagnosis, procedure, admission type or patient ID. Trend, provider, condition and unique-patient analyses are impossible; each row is treated as one beneficiary record, not a verified claim.
* Charges have no stated currency or period.
* Results describe associations in this sample; they do not prove causation or predict savings.
* Anomaly flags are statistical; fraud cannot be determined without labelled cases and richer data.
* One duplicate pair was removed on the assumption of double entry (impact 0.01 %).
* The dataset is a well-known public-style sample; treat conclusions as illustrative for portfolio purposes.

## Reproduce
```bash
git clone <your-repo-url> && cd Healthcare-Insurance-Claims-Analysis
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python Python/run_pipeline.py          # cleans data, writes Dataset/processed/*.csv and Screenshots/python_eda/*.png
python Python/validate_outputs.py      # 29 reconciliation checks
cd Notebooks && jupyter notebook       # open 01_healthcare_claims_analysis.ipynb
```
Then build the dashboard with `PowerBI/dashboard_build_guide.md`.

## Privacy
The file has no names, contact details or direct identifiers; `record_id` is a row number. Do not join this data to identifiable sources.
