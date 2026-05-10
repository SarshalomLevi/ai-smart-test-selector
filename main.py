from src.data.loader import load_data
from src.models.feature_engineering import add_features
from src.models.ml_model import train_model
from src.models.ranking import rank_tests

df = load_data()

df = add_features(df)

model = train_model(df)

ranked_df = rank_tests(model, df)

print(
    ranked_df[
        [
            "test_name",
            "failure_probability"
        ]
    ]
)