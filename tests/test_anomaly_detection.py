import pandas as pd

from src.ml.anomaly_detection import detect_cost_anomalies


def test_detect_cost_anomalies_adds_expected_columns():
    df = pd.DataFrame(
        {
            "Material_Category": ["Steel", "Steel", "Concrete", "Concrete"],
            "Quantity": [10, 12, 15, 1000],
            "Unit_Cost": [100, 105, 80, 5000],
            "Total_Cost": [1000, 1260, 1200, 5000000],
            "Budgeted_Cost": [950, 1200, 1100, 2000],
            "Cost_Variance": [50, 60, 100, 4998000],
            "Cost_Variance_Pct": [5.2, 5.0, 9.1, 249900],
            "Lead_Time_Days": [30, 35, 40, 200],
        }
    )

    result = detect_cost_anomalies(df, contamination=0.25)

    assert "Anomaly_Score" in result.columns
    assert "Is_Anomaly" in result.columns
    assert "Anomaly_Label" in result.columns
    assert "Unit_Cost_vs_Category_Median" in result.columns