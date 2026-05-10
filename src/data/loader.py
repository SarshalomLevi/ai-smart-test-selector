import pandas as pd

def load_data(path="data/test_history.csv"):
    df = pd.read_csv(path)
    return df

if __name__ == "__main__":
    df = load_data()
    print(df.head())