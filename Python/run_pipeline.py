"""End-to-end pipeline: load -> validate -> clean -> analyse -> export (CSV for Power BI, figures, JSON summary).

Usage (from the repository root):
    python Python/run_pipeline.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

import analysis as an
import anomaly as ano
import cleaning as cl
import visuals as vz
from config import AGE_LABELS, BMI_LABELS, PROCESSED_DIR
from data_loader import load_raw


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw = load_raw()
    qr = cl.quality_report(raw)
    df = cl.clean(raw)
    df = ano.add_peer_anomaly_flags(df)

    # ---- Tables ----------------------------------------------------------------
    tables = {
        "summary_age_group": an.group_summary(df, "age_group"),
        "summary_sex": an.group_summary(df, "sex"),
        "summary_smoker": an.group_summary(df, "smoker"),
        "summary_region": an.group_summary(df, "region"),
        "summary_bmi_category": an.group_summary(df, "bmi_category"),
        "summary_children": an.group_summary(df, "children"),
        "summary_smoker_bmi_segment": an.group_summary(df, "smoker_bmi_segment"),
        "summary_charge_band": an.group_summary(df, "charge_band"),
        "segment_region_smoker": an.segment_summary(df, ["region", "smoker"]),
    }
    pearson, spearman = an.correlation_tables(df)
    tests = an.statistical_tests(df)
    model = an.log_linear_model(df)
    overlap = ano.anomaly_overlap(df)

    # ---- Exports for Power BI ------------------------------------------------------
    df.to_csv(PROCESSED_DIR / "claims_clean.csv", index=False)
    df[df["is_high_cost"] | df["is_iqr_outlier"] | df["is_peer_anomaly"]].sort_values(
        "charges", ascending=False).to_csv(PROCESSED_DIR / "flagged_records.csv", index=False)
    for name, t in tables.items():
        t.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)
    tests.to_csv(PROCESSED_DIR / "statistical_tests.csv", index=False)
    model.to_csv(PROCESSED_DIR / "log_linear_model.csv")
    pearson.to_csv(PROCESSED_DIR / "correlation_pearson.csv")
    spearman.to_csv(PROCESSED_DIR / "correlation_spearman.csv")

    # ---- Figures ---------------------------------------------------------------
    vz.charges_distribution(df)
    vz.bar_mean_and_share(df, tables["summary_age_group"], "age_group", "02_age_group", "age group")
    vz.bar_mean_and_share(df, tables["summary_region"], "region", "03_region", "region")
    vz.bar_mean_and_share(df, tables["summary_bmi_category"], "bmi_category", "04_bmi_category", "BMI category")
    vz.smoker_boxplot(df)
    vz.age_bmi_scatter(df)
    vz.correlation_heatmap(pearson, "07_correlation_pearson", "Pearson correlation")
    seg = df.pivot_table(index="smoker", columns="bmi_category", values="charges", aggfunc="mean", observed=True)
    vz.segment_heatmap(seg)
    vz.high_cost_composition(df)
    vz.anomaly_scatter(df)

    # ---- Machine-readable summary (used to validate README numbers) -----------------
    summary = {
        "raw_rows": qr["rows"],
        "exact_duplicates_removed": qr["exact_duplicate_rows"],
        "clean_rows": len(df),
        "kpis": an.kpis(df),
        "iqr_upper_fence": df.attrs["iqr_upper_fence"],
        "iqr_outliers": int(df["is_iqr_outlier"].sum()),
        "peer_anomalies": int(df["is_peer_anomaly"].sum()),
        "peer_anomalies_above": int((df["anomaly_direction"] == "Above peer fence").sum()),
        "peer_anomalies_below": int((df["anomaly_direction"] == "Below peer fence").sum()),
        "model_r2_log_charges": model.attrs["r2"],
    }
    with open(PROCESSED_DIR / "pipeline_summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))
    return df, tables, tests, model, overlap


if __name__ == "__main__":
    main()
