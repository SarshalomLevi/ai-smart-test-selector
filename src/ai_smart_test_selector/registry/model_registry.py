import mlflow


def register_model(run_id: str, model_name: str):

    model_uri = f"runs:/{run_id}/model"

    result = mlflow.register_model(model_uri=model_uri, name=model_name)

    return result
