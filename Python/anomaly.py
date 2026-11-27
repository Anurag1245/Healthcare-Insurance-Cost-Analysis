"""Anomaly detection. IMPORTANT: an anomaly is a statistical flag for review, NOT evidence of fraud.
The dataset has no claim-level fraud labels, providers, dates or diagnoses, so fraud cannot be assessed."""
import numpy as np
import pandas as pd

from config import IQR_MULTIPLIER

PEER_GROUP = ["smoker", "age_group"]


def add_peer_anomaly_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Flag records whose charges are unusual *relative to comparable people* (same smoker status and age group).

    Rule (Tukey fences computed inside each peer group):
        above fence: charges > Q3 + 1.5*IQR     below fence: charges < Q1 - 1.5*IQR
    This differs from the dataset-wide 'high-cost' rule, which only asks 'is it large?'.
    """
    out = df.copy()
    g = out.groupby(PEER_GROUP, observed=True)["charges"]
    q1, q3 = g.transform(lambda s: s.quantile(0.25)), g.transform(lambda s: s.quantile(0.75))
    iqr = q3 - q1
    out["peer_median_charge"] = g.transform("median")
    out["peer_upper_fence"] = q3 + IQR_MULTIPLIER * iqr
    out["charge_vs_peer_median"] = out["charges"] / out["peer_median_charge"]
    above = out["charges"] > out["peer_upper_fence"]
    below = out["charges"] < (q1 - IQR_MULTIPLIER * iqr)
    out["is_peer_anomaly"] = above | below
    out["anomaly_direction"] = np.select([above, below], ["Above peer fence", "Below peer fence"],
                                         default="Within peer range")
    return out


def anomaly_overlap(df: pd.DataFrame) -> pd.DataFrame:
    """How do the three definitions overlap? (high-cost P90 rule, dataset-wide IQR outlier, peer anomaly)"""
    return pd.crosstab([df["is_high_cost"].rename("high_cost_P90"),
                        df["is_iqr_outlier"].rename("iqr_outlier")],
                       df["anomaly_direction"])
