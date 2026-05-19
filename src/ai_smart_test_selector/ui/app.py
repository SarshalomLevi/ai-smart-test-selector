import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import confusion_matrix

from src.data.loader import load_data
from src.models.feature_engineering import add_features
from src.models.ml_model import train_model
from src.models.ranking import rank_tests


# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="AI Smart Test Selector",
    layout="wide"
)

st.title("🧠 AI Smart Test Selector for Firmware Validation")


# -------------------------
# LOAD + PREPROCESS
# -------------------------
df = load_data()
df = add_features(df)


# -------------------------
# TRAIN MODEL
# -------------------------
model, X_test, y_test = train_model(df)


# -------------------------
# RANKING
# -------------------------
ranked_df = rank_tests(model, df)


# -------------------------
# RISK GROUP
# -------------------------
def get_risk_group(risk):
    if risk > 0.85:
        return "CRITICAL"
    elif risk > 0.7:
        return "HIGH"
    elif risk > 0.4:
        return "MEDIUM"
    else:
        return "LOW"


ranked_df["risk_group"] = ranked_df["failure_probability"].apply(get_risk_group)


# -------------------------
# FILTERS
# -------------------------
st.sidebar.header("🎯 Filters")

min_risk = st.sidebar.slider("Min Risk", 0.0, 1.0, 0.0)
max_risk = st.sidebar.slider("Max Risk", 0.0, 1.0, 1.0)

filtered_df = ranked_df[
    (ranked_df["failure_probability"] >= min_risk) &
    (ranked_df["failure_probability"] <= max_risk)
]


# -------------------------
# TABS (RISK FOLDERS)
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔥 CRITICAL", "🔴 HIGH", "🟡 MEDIUM", "🟢 LOW"]
)


# -------------------------
# RENDER FUNCTION
# -------------------------
def render_tests(df):

    for _, row in df.iterrows():

        risk = row["failure_probability"]

        if risk > 0.85:
            risk_label = "🔥 CRITICAL RISK"
        elif risk > 0.7:
            risk_label = "🔴 HIGH RISK"
        elif risk > 0.4:
            risk_label = "🟡 MEDIUM RISK"
        else:
            risk_label = "🟢 LOW RISK"

        title = f"{row['test_name']} | {risk:.2f} | {risk_label}"

        with st.expander(title, expanded=False):

            # -------------------------
            # 1. AI EXPLANATION
            # -------------------------
            st.subheader("🧠 AI Explanation")
            st.info(row.get("explanation", "No explanation available"))

            # -------------------------
            # 2. TEST DATA
            # -------------------------
            st.subheader("📊 Test Data")

            st.dataframe(
                pd.DataFrame({
                    "Metric": [
                        "Runtime (sec)",
                        "Previous Failures",
                        "Run Count",
                        "Severity Score"
                    ],
                    "Value": [
                        row["runtime_sec"],
                        row["previous_failures"],
                        row["run_count"],
                        row["severity_score"]
                    ]
                }),
                use_container_width=True
            )

            # -------------------------
            # 3. RECOMMENDED ACTION
            # -------------------------
            st.subheader("🎯 Recommended Action")

            if risk > 0.85:

                st.error(
                    "🔥 CRITICAL RISK\n"
                    "- Run immediately in smoke testing\n"
                    "- Monitor logs closely\n"
                    "- Escalate if failure repeats"
                )

            elif risk > 0.7:

                st.warning(
                    "HIGH RISK\n"
                    "- Run early in regression\n"
                    "- Prioritize execution"
                )

            elif risk > 0.4:

                st.info(
                    "MEDIUM RISK\n"
                    "- Include in regression suite\n"
                    "- Monitor trends"
                )

            else:

                st.success(
                    "LOW RISK\n"
                    "- Safe for nightly execution\n"
                    "- Low priority"
                )

            st.divider()


# -------------------------
# TAB CONTENT
# -------------------------
with tab1:
    render_tests(filtered_df[filtered_df["failure_probability"] > 0.85])

with tab2:
    render_tests(
        filtered_df[
            (filtered_df["failure_probability"] > 0.7) &
            (filtered_df["failure_probability"] <= 0.85)
        ]
    )

with tab3:
    render_tests(
        filtered_df[
            (filtered_df["failure_probability"] > 0.4) &
            (filtered_df["failure_probability"] <= 0.7)
        ]
    )

with tab4:
    render_tests(
        filtered_df[filtered_df["failure_probability"] <= 0.4]
    )


# -------------------------
# RISK DISTRIBUTION
# -------------------------
st.subheader("📈 Risk Distribution")

st.bar_chart(
    filtered_df.set_index("test_name")[
        "failure_probability"
    ]
)


# -------------------------
# TOP RISKY TESTS
# -------------------------
st.subheader("🔥 Top Risky Tests")

st.dataframe(
    filtered_df.sort_values(
        "failure_probability",
        ascending=False
    ).head(5)
)


# -------------------------
# CONFUSION MATRIX
# -------------------------
st.subheader("📊 Confusion Matrix")

cm = confusion_matrix(y_test, model.predict(X_test))

fig, ax = plt.subplots()

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    ax=ax
)

ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")

st.pyplot(fig)


# -------------------------
# FEATURE IMPORTANCE
# -------------------------
st.subheader("📈 Feature Importance")

importance = model.feature_importances_
features = X_test.columns

df_imp = pd.DataFrame({
    "feature": features,
    "importance": importance
}).sort_values("importance", ascending=False)

fig2, ax2 = plt.subplots()

sns.barplot(
    data=df_imp,
    x="importance",
    y="feature",
    ax=ax2
)

st.pyplot(fig2)


# -------------------------
# EXPORT CSV
# -------------------------
st.subheader("📦 Generate Release Test Suite")

release_df = filtered_df.sort_values(
    "failure_probability",
    ascending=False
).head(5)

csv = release_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Release Test Suite CSV",
    data=csv,
    file_name="release_test_suite.csv",
    mime="text/csv"
)