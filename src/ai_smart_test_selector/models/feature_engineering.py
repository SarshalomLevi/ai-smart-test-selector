def add_features(df):
    # failure rate per test
    df["failure_rate"] = df["previous_failures"] / (df["run_count"] + 1)

    # weighted risk score (simple version)
    df["risk_score"] = (
        df["failure_rate"] * 0.5 +
        df["severity_score"] * 0.5
    )

    return df