def explain_risk(row):
    reasons = []

    if row["previous_failures"] > 5:
        reasons.append("High number of previous failures")

    if row["severity_score"] >= 8:
        reasons.append("High severity test")

    if row["runtime_sec"] > 800:
        reasons.append("Long execution time increases risk")

    if row["run_count"] < 20:
        reasons.append("Low execution history (uncertain behavior)")

    if not reasons:
        reasons.append("Low risk based on historical patterns")

    return " | ".join(reasons)