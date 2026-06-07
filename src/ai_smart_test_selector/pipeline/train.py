import mlflow
import mlflow.sklearn

from mlflow.tracking import MlflowClient

from ai_smart_test_selector.models.ml_model import train_model
from ai_smart_test_selector.pipeline.data import prepare_data
from ai_smart_test_selector.tracking.mlflow_config import setup_mlflow


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

        # 3. Train Models (core logic)
        model, X_test, y_test, results = train_model(df)

        # 4. Compute best model
        best_model_name = max(results.items(), key=lambda x: x[1]["f1"])[0]
        best_metrics = results[best_model_name]

        # 5. Log global metrics
        mlflow.log_metric("best_f1", best_metrics["f1"])
        mlflow.log_metric("best_accuracy", best_metrics["accuracy"])
        mlflow.log_metric("best_precision", best_metrics["precision"])
        mlflow.log_metric("best_recall", best_metrics["recall"])

        # 6. Log all models metrics
        for name, metrics in results.items():
            mlflow.log_metric(f"{name}_f1", metrics["f1"])
            mlflow.log_metric(f"{name}_accuracy", metrics["accuracy"])
            mlflow.log_metric(f"{name}_precision", metrics["precision"])
            mlflow.log_metric(f"{name}_recall", metrics["recall"])

        # 7. Log and register model
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="test-risk-model",
        )

        # =====================================================
        # 8. PROMOTE MODEL TO PRODUCTION (MLFLOW REGISTRY)
        # =====================================================
        client = MlflowClient()

        # get latest model version
        latest_version = client.get_latest_versions(
            name="test-risk-model", stages=["None"]
        )[0].version

        # transition to Production
        client.transition_model_version_stage(
            name="test-risk-model", version=latest_version, stage="Production"
        )

        # 9. Summary
        print("\n==============================")
        print("MLflow Run Completed ✔")
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
