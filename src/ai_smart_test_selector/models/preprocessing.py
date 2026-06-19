import pandas as pd


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encodes categorical features into numerical format
    for ML training (Firmware Validation dataset V2).
    """

    categorical_cols = [
        "module",
        "subsystem",
        "hardware_revision",
        "test_type",
        "environment",
    ]

    # Safety check: ensure columns exist (avoids crashes in pipeline)
    existing_cols = [col for col in categorical_cols if col in df.columns]

    # One-hot encoding
    df = pd.get_dummies(df, columns=existing_cols)

    return df
