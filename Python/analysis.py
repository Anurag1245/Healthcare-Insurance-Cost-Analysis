"""KPIs, grouped summaries, correlation and statistical tests."""
import numpy as np
import pandas as pd
from scipy import stats


def kpis(df: pd.DataFrame) -> dict:
    return {
        "records": int(len(df)),
        "total_charges": float(df["charges"].sum()),
        "average_charge": float(df["charges"].mean()),
        "median_charge": float(df["charges"].median()),
        "highest_charge": float(df["charges"].max()),
        "lowest_charge": float(df["charges"].min()),
        "std_charge": float(df["charges"].std()),
        "high_cost_threshold": float(df.attrs.get("high_cost_threshold", np.nan)),
        "high_cost_records": int(df["is_high_cost"].sum()),
        "high_cost_share_of_total": float(df.loc[df["is_high_cost"], "charges"].sum() / df["charges"].sum()),
    }


def group_summary(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Count, total, mean, median, share of records & share of cost for one category."""
    g = (df.groupby(by, observed=True)["charges"]
           .agg(records="count", total_charges="sum", mean_charge="mean",
                median_charge="median", max_charge="max").reset_index())
    g["pct_of_records"] = g["records"] / g["records"].sum() * 100
    g["pct_of_total_charges"] = g["total_charges"] / g["total_charges"].sum() * 100
    high = df.groupby(by, observed=True)["is_high_cost"].sum().reset_index(name="high_cost_records")
    g = g.merge(high, on=by)
    g["high_cost_rate_pct"] = g["high_cost_records"] / g["records"] * 100
    return g.round(2)


def segment_summary(df: pd.DataFrame, by: list) -> pd.DataFrame:
    g = (df.groupby(by, observed=True)["charges"]
           .agg(records="count", mean_charge="mean", median_charge="median",
                total_charges="sum").reset_index())
    g["pct_of_total_charges"] = g["total_charges"] / g["total_charges"].sum() * 100
    return g.round(2)


def correlation_tables(df: pd.DataFrame):
    num = df[["age", "bmi", "children", "smoker_flag", "charges"]]
    return num.corr(method="pearson").round(3), num.corr(method="spearman").round(3)


def statistical_tests(df: pd.DataFrame) -> pd.DataFrame:
    """Non-parametric tests (charges are strongly right-skewed). Associations only, not causation."""
    rows = []

    def mw(label, a, b):
        stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        # rank-biserial effect size
        r = 1 - 2 * stat / (len(a) * len(b))
        rows.append([label, "Mann-Whitney U", p, abs(r), "rank-biserial |r|"])

    def kw(label, groups):
        h, p = stats.kruskal(*groups)
        eps2 = h / (sum(len(g) for g in groups) - 1)
        rows.append([label, "Kruskal-Wallis H", p, eps2, "epsilon-squared"])

    mw("Charges: smokers vs non-smokers", df.loc[df.smoker == "yes", "charges"], df.loc[df.smoker == "no", "charges"])
    mw("Charges: male vs female", df.loc[df.sex == "male", "charges"], df.loc[df.sex == "female", "charges"])
    kw("Charges across regions", [g["charges"].values for _, g in df.groupby("region", observed=True)])
    kw("Charges across BMI categories", [g["charges"].values for _, g in df.groupby("bmi_category", observed=True)])
    kw("Charges across age groups", [g["charges"].values for _, g in df.groupby("age_group", observed=True)])
    kw("Charges across number of children", [g["charges"].values for _, g in df.groupby("children")])
    out = pd.DataFrame(rows, columns=["comparison", "test", "p_value", "effect_size", "effect_size_type"])
    out["significant_at_5pct"] = out["p_value"] < 0.05
    return out


def design_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Design matrix shared by the regression and the anomaly detector.
    Includes a smoker x obese interaction because the data show the cost effect of obesity is concentrated in smokers."""
    X = pd.DataFrame({
        "intercept": 1.0,
        "age": df["age"],
        "bmi": df["bmi"],
        "children": df["children"],
        "smoker": df["smoker_flag"],
        "male": (df["sex"] == "male").astype(int),
        "obese": (df["bmi"] >= 30).astype(int),
        "smoker_x_obese": df["smoker_flag"] * (df["bmi"] >= 30).astype(int),
    })
    return pd.concat([X, pd.get_dummies(df["region"], prefix="region", drop_first=True, dtype=float)], axis=1)


def log_linear_model(df: pd.DataFrame) -> pd.DataFrame:
    """OLS on log(charges) using numpy only. pct_effect = exp(coef)-1 (approximate % change in charges).
    Observational associations only; not causal."""
    X = design_matrix(df)
    y = df["log_charges"].values
    beta, *_ = np.linalg.lstsq(X.values, y, rcond=None)
    resid = y - X.values @ beta
    n, k = X.shape
    sigma2 = resid @ resid / (n - k)
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(X.values.T @ X.values)))
    r2 = 1 - resid @ resid / ((y - y.mean()) @ (y - y.mean()))
    res = pd.DataFrame({"coef": beta, "std_err": se, "t": beta / se,
                        "pct_effect": (np.exp(beta) - 1) * 100}, index=X.columns).round(4)
    res.attrs["r2"] = float(r2)
    res.attrs["n"] = n
    return res
