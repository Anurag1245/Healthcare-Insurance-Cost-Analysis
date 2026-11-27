"""Load the raw dataset and validate its schema."""
import pandas as pd

from config import EXPECTED_COLUMNS, RAW_FILE


def load_raw(path=RAW_FILE) -> pd.DataFrame:
    """Read the raw CSV and fail loudly if the schema differs from what the project expects."""
    df = pd.read_csv(path)
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    extra = set(df.columns) - set(EXPECTED_COLUMNS)
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {sorted(missing)}")
    if extra:
        print(f"[warn] Unexpected extra columns will be ignored by the pipeline: {sorted(extra)}")
    return df[EXPECTED_COLUMNS].copy()
