def rank_tests(model, df):

    X = df[
        [
            "runtime_sec",
            "previous_failures",
            "run_count",
            "severity_score"
        ]
    ]

    # probability of failure
    probabilities = model.predict_proba(X)[:, 1]

    df["failure_probability"] = probabilities

    ranked_df = df.sort_values(
        by="failure_probability",
        ascending=False
    )

    return ranked_df