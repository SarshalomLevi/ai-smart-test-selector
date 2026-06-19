from ai_smart_test_selector.data.loader import load_data
from ai_smart_test_selector.models.feature_engineering import add_features
from ai_smart_test_selector.models.preprocessing import preprocess_data


def prepare_data():

    df = load_data()

    df = add_features(df)

    df = preprocess_data(df)

    return df
