def add_features(df):

    # Normalize code churn
    df["normalized_churn"] = df["code_churn_module"] / 100

    # recent bug signal
    df["recent_bug_signal"] = 1 / (df["last_bug_age_days"] + 1)

    # environment risk
    df["environment_risk"] = df["environment"].map({"emu": 0.2, "real_hw": 1.0})

    # firmware release risk
    df["firmware_risk"] = df["firmware_version"] / df["firmware_version"].max()

    # composite risk feature
    df["risk_score"] = (
        0.30 * df["previous_fail_rate"]
        + 0.20 * df["flaky_score"]
        + 0.20 * df["normalized_churn"]
        + 0.15 * df["environment_risk"]
        + 0.15 * df["recent_bug_signal"]
    )

    return df
