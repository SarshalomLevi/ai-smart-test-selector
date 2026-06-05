from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
)

from sklearn.linear_model import LogisticRegression


def train_model(df):

    X = df[
        [
            "runtime_sec",
            "previous_failures",
            "run_count",
            "severity_score",
        ]
    ]

    y = df["failed"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y,
    )

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            random_state=42,
        ),
        "GradientBoosting": GradientBoostingClassifier(),
    }

    results = {}

    best_model = None
    best_f1 = 0

    for name, model in models.items():

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        results[name] = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

        print(f"\n{name}")
        print(f"Accuracy : {accuracy:.3f}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall   : {recall:.3f}")
        print(f"F1 Score : {f1:.3f}")

        if f1 > best_f1:
            best_f1 = f1
            best_model = model

    print("\nBEST MODEL F1:", best_f1)

    return best_model, X_test, y_test, results
