"""Central configuration: paths, business definitions and plotting defaults."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "Dataset" / "insurance.csv"
PROCESSED_DIR = ROOT / "Dataset" / "processed"
FIGURE_DIR = ROOT / "Screenshots" / "python_eda"
DOC_DIR = ROOT / "Documentation"

# ---- Expected schema (validated on load; the project never assumes other columns) ----
EXPECTED_COLUMNS = ["age", "sex", "bmi", "children", "smoker", "region", "charges"]

# ---- Business definitions -------------------------------------------------------
AGE_BINS = [17, 24, 34, 44, 54, 64]
AGE_LABELS = ["18-24", "25-34", "35-44", "45-54", "55-64"]

# WHO adult BMI categories
BMI_BINS = [0, 18.5, 25, 30, float("inf")]
BMI_LABELS = ["Underweight", "Normal", "Overweight", "Obese"]

# "High-cost" = top decile of charges (business rule, adjustable here)
HIGH_COST_PERCENTILE = 0.90
# Statistical outlier fence = Tukey IQR rule
IQR_MULTIPLIER = 1.5
# Peer anomaly = Tukey fences computed within smoker x age-group peer sets

RANDOM_SEED = 42
