from src.data.loader import load_data
from src.models.feature_engineering import add_features
from src.models.ml_model import train_model
from src.evaluation.evaluate_model import evaluate_model

df = load_data()

df = add_features(df)

model, X_test, y_test = train_model(df)

evaluate_model(model, X_test, y_test)