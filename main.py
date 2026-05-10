from src.data.loader import load_data
from src.models.feature_engineering import add_features
from src.models.ml_model import train_model

df = load_data()
df = add_features(df)

print(df[["test_name", "failure_rate", "risk_score"]])

model = train_model(df)