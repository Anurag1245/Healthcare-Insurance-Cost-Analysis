"""Independent validation of pipeline outputs. Run after run_pipeline.py; exits non-zero on any failed check."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from config import PROCESSED_DIR, RAW_FILE


def check(name, condition):
    print(("PASS  " if condition else "FAIL  ") + name)
    return bool(condition)


def main():
    raw = pd.read_csv(RAW_FILE)
    clean = pd.read_csv(PROCESSED_DIR / "claims_clean.csv")
    results = []

    results.append(check("clean rows = raw rows - exact duplicates",
                         len(clean) == len(raw) - raw.duplicated().sum()))
    results.append(check("no missing values after cleaning", clean[["age", "sex", "bmi", "children", "smoker", "region", "charges"]].isna().sum().sum() == 0))
    results.append(check("total charges reconcile with raw (minus removed duplicate)",
                         np.isclose(clean["charges"].sum(), raw.drop_duplicates()["charges"].sum())))
    results.append(check("record_id is unique", clean["record_id"].is_unique))

    for name, key in [("summary_age_group", "age_group"), ("summary_sex", "sex"), ("summary_smoker", "smoker"),
                      ("summary_region", "region"), ("summary_bmi_category", "bmi_category"),
                      ("summary_children", "children"), ("summary_smoker_bmi_segment", "smoker_bmi_segment")]:
        t = pd.read_csv(PROCESSED_DIR / f"{name}.csv")
        results.append(check(f"{name}: records sum to total", t["records"].sum() == len(clean)))
        results.append(check(f"{name}: total_charges sum to grand total (rounded to 2 dp per row)",
                             abs(t["total_charges"].sum() - clean["charges"].sum()) < 0.01 * len(t) + 0.01))
        results.append(check(f"{name}: % of total charges sums to ~100", abs(t["pct_of_total_charges"].sum() - 100) < 0.1))

    p90 = clean["charges"].quantile(0.90)
    results.append(check("high-cost flag matches P90 rule", (clean["is_high_cost"] == (clean["charges"] > p90)).all()))
    results.append(check("age groups cover every record", clean["age_group"].notna().all()))
    results.append(check("BMI categories cover every record", clean["bmi_category"].notna().all()))
    results.append(check("charges are all positive", (clean["charges"] > 0).all()))

    if not all(results):
        print("\nValidation FAILED")
        sys.exit(1)
    print(f"\nAll {len(results)} validation checks passed.")


if __name__ == "__main__":
    main()
