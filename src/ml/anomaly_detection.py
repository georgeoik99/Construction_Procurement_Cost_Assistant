import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


ANOMALY_FEATURES = [
    "Quantity",
    "Unit_Cost",
    "Total_Cost",
    "Budgeted_Cost",
    "Cost_Variance",
    "Cost_Variance_Pct",
    "Lead_Time_Days",
]


def detect_cost_anomalies(
    df: pd.DataFrame,
    contamination: float = 0.05,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Detect unusual procurement cost records using Isolation Forest.

    The model flags purchase orders with unusual cost, variance, quantity,
    or lead-time behavior.
    """

    df = df.copy()

    missing_features = [col for col in ANOMALY_FEATURES if col not in df.columns]

    if missing_features:
        raise ValueError(f"Missing anomaly detection features: {missing_features}")

    model_input = df[ANOMALY_FEATURES].copy()
    model_input = model_input.apply(pd.to_numeric, errors="coerce")
    model_input = model_input.fillna(model_input.median())

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(model_input)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state,
    )

    predictions = model.fit_predict(scaled_features)
    anomaly_scores = model.decision_function(scaled_features)

    df["Anomaly_Score"] = anomaly_scores
    df["Is_Anomaly"] = predictions == -1
    df["Anomaly_Label"] = df["Is_Anomaly"].map(
        {
            True: "Anomaly",
            False: "Normal",
        }
    )

    df["Category_Median_Unit_Cost"] = df.groupby("Material_Category")[
        "Unit_Cost"
    ].transform("median")

    df["Unit_Cost_vs_Category_Median"] = (
        df["Unit_Cost"] / df["Category_Median_Unit_Cost"]
    ).round(2)

    return df.sort_values("Anomaly_Score")