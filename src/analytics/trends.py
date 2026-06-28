import pandas as pd


def monthly_procurement_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return monthly procurement cost and PO volume trends.
    """

    return (
        df.groupby("PO_Month", as_index=False)
        .agg(
            Total_Cost=("Total_Cost", "sum"),
            PO_Count=("PO_Number", "nunique"),
            Avg_Lead_Time_Days=("Lead_Time_Days", "mean"),
            Avg_Cost_Variance_Pct=("Cost_Variance_Pct", "mean"),
        )
        .sort_values("PO_Month")
    )


def monthly_category_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return monthly cost trends by material category.
    """

    return (
        df.groupby(["PO_Month", "Material_Category"], as_index=False)
        .agg(
            Total_Cost=("Total_Cost", "sum"),
            PO_Count=("PO_Number", "nunique"),
        )
        .sort_values(["PO_Month", "Total_Cost"], ascending=[True, False])
    )