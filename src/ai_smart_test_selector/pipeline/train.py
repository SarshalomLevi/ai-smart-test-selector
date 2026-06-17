import mlflow
import mlflow.sklearn

from mlflow.tracking import MlflowClient

from ai_smart_test_selector.models.ml_model import train_model
from ai_smart_test_selector.pipeline.data import prepare_data
from ai_smart_test_selector.tracking.mlflow_config import setup_mlflow

import sys

sys.stdout.reconfigure(encoding="utf-8")


# =========================
# TRAINING PIPELINE
# =========================
def run_training_pipeline():

    setup_mlflow()

    # 1. Load Data
    df = prepare_data()

    # 2. Start MLflow Run
    with mlflow.start_run() as run:

        run_id = run.info.run_id

        # 3. Train Models
        model, X_test, y_test, results, *_ = train_model(df)

        # 4. Compute best model
        best_model_name = max(results.items(), key=lambda x: x[1]["f1"])[0]
        best_metrics = results[best_model_name]

        # 5. Log best metrics
        mlflow.log_metrics(
            {
                "best_f1": best_metrics["f1"],
                "best_accuracy": best_metrics["accuracy"],
                "best_precision": best_metrics["precision"],
                "best_recall": best_metrics["recall"],
            }
        )

        # 6. Log all models metrics
        for name, metrics in results.items():
            mlflow.log_metrics(
                {
                    f"{name}_f1": metrics["f1"],
                    f"{name}_accuracy": metrics["accuracy"],
                    f"{name}_precision": metrics["precision"],
                    f"{name}_recall": metrics["recall"],
                }
            )

        # 7. Log model + register
        mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            registered_model_name="test-risk-model",
        )

        # =====================================================
        # 8. PROMOTE MODEL TO PRODUCTION (SAFE REGISTRY FLOW)
        # =====================================================
        client = MlflowClient()

        try:
            versions = client.search_model_versions("name='test-risk-model'")

            if not versions:
                raise ValueError("No registered model versions found")

            latest_version = max(versions, key=lambda v: int(v.version)).version

            client.transition_model_version_stage(
                name="test-risk-model", version=latest_version, stage="Production"
            )

        except Exception as e:
            print(f"[WARNING] Model promotion failed: {e}")
            latest_version = None

        # 9. Summary
        print("\n==============================")
        print("MLflow Run Completed [OK]")
        print("Run ID:", run_id)
        print("Best Model:", best_model_name)
        print("Best F1:", best_metrics["f1"])
        print("Promoted Version:", latest_version)
        print("==============================\n")

        return {
            "run_id": run_id,
            "model": model,
            "best_model": best_model_name,
            "best_f1": best_metrics["f1"],
            "results": results,
            "production_version": latest_version,
        }


# =========================
# CLI ENTRY POINT
# =========================
if __name__ == "__main__":
    run_training_pipeline()
