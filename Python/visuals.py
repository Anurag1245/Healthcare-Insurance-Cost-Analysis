"""Reusable plotting functions. Every function saves a PNG and returns the figure path."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from config import FIGURE_DIR

sns.set_theme(style="whitegrid", context="notebook")
PALETTE = {"yes": "#D1495B", "no": "#2E86AB"}


def _save(fig, name):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURE_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def charges_distribution(df):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(df["charges"], bins=40, kde=True, ax=ax[0], color="#2E86AB")
    ax[0].set(title="Distribution of charges (right-skewed)", xlabel="Charges")
    sns.histplot(df["log_charges"], bins=40, kde=True, ax=ax[1], color="#6C757D")
    ax[1].set(title="Distribution of log(charges)", xlabel="log(Charges)")
    return _save(fig, "01_charges_distribution")


def bar_mean_and_share(df, summary, by, name, title):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    sns.barplot(data=summary, x=by, y="mean_charge", ax=ax[0], color="#2E86AB")
    ax[0].set(title=f"Average charge by {title}", ylabel="Average charge", xlabel="")
    sns.barplot(data=summary, x=by, y="pct_of_total_charges", ax=ax[1], color="#F18F01")
    ax[1].set(title=f"Share of total charges by {title}", ylabel="% of total charges", xlabel="")
    for a in ax:
        a.tick_params(axis="x", rotation=20)
    return _save(fig, name)


def smoker_boxplot(df):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.boxplot(data=df, x="smoker", y="charges", hue="smoker", palette=PALETTE, legend=False, ax=ax)
    ax.set(title="Charges by smoker status", xlabel="Smoker", ylabel="Charges")
    return _save(fig, "05_smoker_boxplot")


def age_bmi_scatter(df):
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    sns.scatterplot(data=df, x="age", y="charges", hue="smoker", palette=PALETTE, alpha=.6, ax=ax[0])
    ax[0].set(title="Charges vs age (by smoker status)")
    sns.scatterplot(data=df, x="bmi", y="charges", hue="smoker", palette=PALETTE, alpha=.6, ax=ax[1])
    ax[1].axvline(30, ls="--", color="grey")
    ax[1].set(title="Charges vs BMI (dashed = BMI 30)")
    return _save(fig, "06_age_bmi_scatter")


def correlation_heatmap(corr, name, title):
    fig, ax = plt.subplots(figsize=(6, 4.8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax)
    ax.set_title(title)
    return _save(fig, name)


def segment_heatmap(seg_table):
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.heatmap(seg_table, annot=True, fmt=",.0f", cmap="YlOrRd", ax=ax)
    ax.set_title("Average charge: smoker x BMI category")
    return _save(fig, "08_smoker_bmi_heatmap")


def high_cost_composition(df):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    comp = (df.groupby(["is_high_cost", "smoker"], observed=True).size().unstack(fill_value=0))
    comp = comp.div(comp.sum(axis=1), axis=0) * 100
    comp.index = ["Not high-cost", "High-cost (top 10%)"]
    comp.plot(kind="bar", stacked=True, color=[PALETTE["no"], PALETTE["yes"]], ax=ax)
    ax.set(title="Smoker mix: high-cost vs other records", ylabel="% of records", xlabel="")
    ax.tick_params(axis="x", rotation=0)
    return _save(fig, "09_high_cost_composition")


def anomaly_scatter(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    base = df[df["anomaly_direction"] == "Within peer range"]
    flagged = df[df["is_peer_anomaly"]]
    ax.scatter(base["age"], base["charges"], s=12, alpha=.4, color="#9AA5B1", label="Within peer range")
    ax.scatter(flagged["age"], flagged["charges"], s=35, color="#D1495B", label="Peer anomaly (review)")
    ax.set(title="Peer-relative anomalies (flag for review, not fraud)", xlabel="Age", ylabel="Charges")
    ax.legend()
    return _save(fig, "10_peer_anomalies")
