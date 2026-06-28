import pandas as pd


def supplier_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a supplier-level scorecard based on spend, delivery delay, 
    cost variance, and risk exposure.
    """

    supplier_df = (
        df.groupby("Supplier_Name", as_index=False)
        .agg(
            Total_Cost=("Total_Cost", "sum"),
            PO_Count=("PO_Number", "nunique"),
            Avg_Lead_Time_Days=("Lead_Time_Days", "mean"),
            Avg_Cost_Variance_Pct=("Cost_Variance_Pct", "mean"),
            High_Risk_Orders=("Risk_Level", lambda x: (x == "High").sum()),
        )
    )

    supplier_df["Risk_Flag"] = supplier_df.apply(_assign_supplier_risk, axis=1)

    return supplier_df.sort_values(
        ["Risk_Flag", "Total_Cost"],
        ascending=[True, False],
    )


def _assign_supplier_risk(row: pd.Series) -> str:
    """
    Assign a simple business risk flag to each supplier.
    """

    if (
        row["High_Risk_Orders"] >= 5
        or row["Avg_Cost_Variance_Pct"] > 15
        or row["Avg_Lead_Time_Days"] > 80
    ):
        return "High"

    if (
        row["High_Risk_Orders"] >= 2
        or row["Avg_Cost_Variance_Pct"] > 7
        or row["Avg_Lead_Time_Days"] > 60
    ):
        return "Medium"

    return "Low"