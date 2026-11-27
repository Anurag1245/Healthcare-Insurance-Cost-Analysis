"""Data quality checks, cleaning and feature engineering."""
import numpy as np
import pandas as pd

from config import (AGE_BINS, AGE_LABELS, BMI_BINS, BMI_LABELS,
                    HIGH_COST_PERCENTILE, IQR_MULTIPLIER)


def quality_report(df: pd.DataFrame) -> dict:
    """Collect data-quality facts about the *raw* data (no changes made)."""
    dup_mask = df.duplicated(keep=False)
    report = {
        "rows": len(df),
        "columns": df.shape[1],
        "missing_total": int(df.isna().sum().sum()),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "duplicate_rows_involved": df[dup_mask].copy(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "sex_values": sorted(df["sex"].unique()),
        "smoker_values": sorted(df["smoker"].unique()),
        "region_values": sorted(df["region"].unique()),
        "age_range": (int(df["age"].min()), int(df["age"].max())),
        "bmi_range": (float(df["bmi"].min()), float(df["bmi"].max())),
        "children_range": (int(df["children"].min()), int(df["children"].max())),
        "charges_non_positive": int((df["charges"] <= 0).sum()),
        "bmi_non_positive": int((df["bmi"] <= 0).sum()),
    }
    return report


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return an analysis-ready dataframe with engineered columns."""
    out = df.copy()

    # Standardise text and set categorical types
    for col in ["sex", "smoker", "region"]:
        out[col] = out[col].str.strip().str.lower()
    out["sex"] = out["sex"].astype("category")
    out["smoker"] = out["smoker"].astype("category")
    out["region"] = out["region"].astype("category")

    # Exact duplicates: all 7 fields (incl. charges to 4 decimals) identical -> treated as double entry
    out = out.drop_duplicates(keep="first").reset_index(drop=True)

    # Surrogate key. The raw data has NO patient/claim ID, so this is a row id only.
    out.insert(0, "record_id", np.arange(1, len(out) + 1))

    # Analytical columns
    out["age_group"] = pd.cut(out["age"], bins=AGE_BINS, labels=AGE_LABELS)
    out["bmi_category"] = pd.cut(out["bmi"], bins=BMI_BINS, labels=BMI_LABELS, right=False)
    out["has_children"] = np.where(out["children"] > 0, "Yes", "No")
    out["smoker_flag"] = (out["smoker"] == "yes").astype(int)
    out["log_charges"] = np.log(out["charges"])

    # High-cost (business rule) vs statistical outlier (Tukey fence) are kept separate on purpose
    p_high = out["charges"].quantile(HIGH_COST_PERCENTILE)
    q1, q3 = out["charges"].quantile([0.25, 0.75])
    fence = q3 + IQR_MULTIPLIER * (q3 - q1)
    out["is_high_cost"] = out["charges"] > p_high
    out["is_iqr_outlier"] = out["charges"] > fence
    out.attrs["high_cost_threshold"] = float(p_high)
    out.attrs["iqr_upper_fence"] = float(fence)

    out["charge_band"] = pd.cut(
        out["charges"], bins=[0, 5000, 10000, 20000, 40000, np.inf],
        labels=["<5K", "5K-10K", "10K-20K", "20K-40K", "40K+"])
    out["smoker_bmi_segment"] = (
        np.where(out["smoker"] == "yes", "Smoker", "Non-smoker") + " / "
        + np.where(out["bmi"] >= 30, "Obese", "Non-obese"))
    return out
