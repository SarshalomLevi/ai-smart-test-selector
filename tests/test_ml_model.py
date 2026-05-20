from ai_smart_test_selector.data.loader import load_data
from ai_smart_test_selector.models.ml_model import train_model


# Ensures the training pipeline runs successfully without errors.
def test_model_training():

    df = load_data()

    model, X_test, y_test = train_model(df)

    assert model is not None

    assert len(X_test) > 0

    assert len(y_test) > 0

# Ensures the trained model can make predictions.
def test_model_prediction():

    df = load_data()

    model, X_test, y_test = train_model(df)

    predictions = model.predict(X_test)

    assert len(predictions) == len(y_test)
    assert set(predictions).issubset({0, 1})
    