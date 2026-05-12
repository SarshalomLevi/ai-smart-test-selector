from src.models.explainability import explain_risk

def rank_tests(model, df):

    X = df[
        [
            "runtime_sec",
            "previous_failures",
            "run_count",
            "severity_score"
        ]
    ]

    probabilities = model.predict_proba(X)[:, 1]

    df = df.copy()
    df["failure_probability"] = probabilities

    # 🧠 Explainability (clean version)
    df["explanation"] = df.apply(explain_risk, axis=1)

    return df.sort_values("failure_probability", ascending=False)