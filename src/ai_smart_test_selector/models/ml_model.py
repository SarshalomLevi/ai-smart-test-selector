from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
)

# Advanced models (optional but industry-level)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier


# =========================
# TRAIN MODEL PIPELINE
# =========================
def train_model(df):

    # -------------------------
    # Features & Target
    # -------------------------
    X = df[
        [
            "runtime_sec",
            "previous_failures",
            "run_count",
            "severity_score",
        ]
    ]

    y = df["failed"]

    # -------------------------
    # Train/Test Split
    # -------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y,
    )

    # -------------------------
    # Models Pool
    # -------------------------
    models = {
        "logreg": LogisticRegression(max_iter=1000),
        "rf": RandomForestClassifier(
            n_estimators=100,
            random_state=42,
        ),
        "gb": GradientBoostingClassifier(),
        "extra_trees": ExtraTreesClassifier(random_state=42),
        "xgb": XGBClassifier(
            eval_metric="logloss",
            random_state=42,
        ),
        "lgbm": LGBMClassifier(),
        "catboost": CatBoostClassifier(verbose=0),
    }

    results = {}

    best_model = None
    best_name = None
    best_f1 = -1

    # -------------------------
    # Training Loop
    # -------------------------
    for name, model in models.items():

        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds),
            "recall": recall_score(y_test, preds),
            "f1": f1_score(y_test, preds),
        }

        results[name] = {
            "model": model,
            **metrics,
        }

        print(f"\n{name}")
        print(f"Accuracy : {metrics['accuracy']:.3f}")
        print(f"Precision: {metrics['precision']:.3f}")
        print(f"Recall   : {metrics['recall']:.3f}")
        print(f"F1 Score : {metrics['f1']:.3f}")

        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            best_model = model
            best_name = name

    # -------------------------
    # Summary
    # -------------------------
    print("\n=========================")
    print("BEST MODEL:", best_name)
    print("BEST F1   :", best_f1)
    print("=========================\n")

    # -------------------------
    # Return for pipeline / MLflow
    # -------------------------
    return best_model, X_test, y_test, results, best_name
