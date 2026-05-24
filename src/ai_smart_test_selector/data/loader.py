from pathlib import Path
import pandas as pd


def load_data(path=None):
    if path is None:
        base_dir = Path(__file__).resolve().parents[3]
        path = (
            base_dir
            / "src"
            / "ai_smart_test_selector"
            / "data"
            / "test_history.csv"
        )

    return pd.read_csv(path)
