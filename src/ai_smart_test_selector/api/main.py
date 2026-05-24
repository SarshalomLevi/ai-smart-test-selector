from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd

from src.data.loader import load_data
from src.models.feature_engineering import add_features
from src.models.ml_model import train_model
from src.models.ranking import rank_tests


# =========================================================
# FASTAPI APPLICATION INITIALIZATION
# =========================================================
app = FastAPI(
    title="AI Smart Test Selector API"
)


# =========================================================
# INPUT SCHEMA FOR ML PREDICTION
# =========================================================
class TestInput(BaseModel):

    runtime_sec: int = Field(
        example=600,
        description="Total execution time of the test in seconds"
    )

    previous_failures: int = Field(
        example=5,
        description="Number of previous failures recorded for this test"
    )

    run_count: int = Field(
        example=10,
        description="Total number of times the test was executed"
    )

    severity_score: int = Field(
        example=9,
        description="Severity level of the test (1-10 scale)"
    )


# =========================================================
# LOAD DATA + FEATURE ENGINEERING + MODEL TRAINING
# =========================================================

# Load raw dataset
df = load_data()

# Apply feature engineering transformations
df = add_features(df)

# Train ML model
model, X_test, y_test = train_model(df)

# Precompute ranked test results (IMPORTANT: done once for performance)
ranked_df = rank_tests(model, df)


# =========================================================
# ROOT ENDPOINT (HEALTH CHECK)
# =========================================================
@app.get("/")
def root():

    return {
        "message": "AI Smart Test Selector API is running"
    }


# =========================================================
# GET FULL RANKED TEST LIST
# =========================================================
@app.get("/rank-tests")
def rank_all_tests():

    # Return all tests with predicted risk and explanation
    return ranked_df[
        [
            "test_name",
            "failure_probability",
            "explanation"
        ]
    ].to_dict(orient="records")


# =========================================================
# GET AVAILABLE TEST NAMES
# =========================================================
@app.get("/available-tests")
def available_tests():

    # Used by UI / CI systems to know valid test identifiers
    return {
        "tests": ranked_df["test_name"].tolist()
    }


# =========================================================
# GET TOP RISKY TESTS
# =========================================================
@app.get("/top-risky")
def top_risky_tests():

    # Sort by highest failure probability
    top_df = ranked_df.sort_values(
        "failure_probability",
        ascending=False
    ).head(5)

    return top_df[
        [
            "test_name",
            "failure_probability",
            "explanation"
        ]
    ].to_dict(orient="records")


# =========================================================
# GET ONLY CRITICAL TESTS (CI/CD USAGE)
# =========================================================
@app.get("/critical-tests")
def critical_tests():

    # Filter only high-risk tests for CI pipelines
    critical_df = ranked_df[
        ranked_df["failure_probability"] > 0.7
    ]

    return critical_df[
        [
            "test_name",
            "failure_probability",
            "explanation"
        ]
    ].to_dict(orient="records")


# =========================================================
# SIMULATE SINGLE TEST EXECUTION
# =========================================================
@app.get("/simulate-test/{test_name}")
def simulate_test(test_name: str):

    # Find test in ranked dataset
    selected = ranked_df[
        ranked_df["test_name"] == test_name
    ]

    # Handle missing test case
    if selected.empty:
        return {
            "error": "Test not found"
        }

    row = selected.iloc[0]

    risk = float(row["failure_probability"])

    # Risk classification logic
    if risk > 0.85:
        result = "CRITICAL"
    elif risk > 0.7:
        result = "FAILED"
    elif risk > 0.4:
        result = "UNSTABLE"
    else:
        result = "PASSED"

    return {
        "test_name": row["test_name"],
        "risk": round(risk, 2),
        "result": result,
        "explanation": row["explanation"]
    }


# =========================================================
# MACHINE LEARNING PREDICTION ENDPOINT
# =========================================================
@app.post("/predict")
def predict(test: TestInput):

    # Convert input to DataFrame for model inference
    input_df = pd.DataFrame(
        [{
            "runtime_sec": test.runtime_sec,
            "previous_failures": test.previous_failures,
            "run_count": test.run_count,
            "severity_score": test.severity_score
        }]
    )

    # Predict failure probability
    probability = model.predict_proba(input_df)[0][1]

    # Generate human-readable explanation
    if probability > 0.85:
        explanation = "Critical risk due to severe instability"
    elif probability > 0.7:
        explanation = "High risk due to frequent failures"
    elif probability > 0.4:
        explanation = "Medium risk due to unstable behavior"
    else:
        explanation = "Low risk and stable history"

    return {
        "failure_probability": round(float(probability), 2),
        "explanation": explanation
    }
