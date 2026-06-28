import pandas as pd


def total_cost_by_supplier(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Return suppliers ranked by total procurement cost.
    """

    return (
        df.groupby("Supplier_Name", as_index=False)
        .agg(
            Total_Cost=("Total_Cost", "sum"),
            PO_Count=("PO_Number", "nunique"),
            Avg_Unit_Cost=("Unit_Cost", "mean"),
        )
        .sort_values("Total_Cost", ascending=False)
        .head(top_n)
    )


def total_cost_by_project(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Return projects ranked by total procurement cost.
    """

    return (
        df.groupby("Project_Name", as_index=False)
        .agg(
            Total_Cost=("Total_Cost", "sum"),
            PO_Count=("PO_Number", "nunique"),
            Avg_Cost_Variance_Pct=("Cost_Variance_Pct", "mean"),
        )
        .sort_values("Total_Cost", ascending=False)
        .head(top_n)
    )


def total_cost_by_material_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return total cost by material category.
    """

    return (
        df.groupby("Material_Category", as_index=False)
        .agg(
            Total_Cost=("Total_Cost", "sum"),
            PO_Count=("PO_Number", "nunique"),
            Avg_Lead_Time_Days=("Lead_Time_Days", "mean"),
        )
        .sort_values("Total_Cost", ascending=False)
    )


def cost_overrun_by_project(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Return projects ranked by total cost variance.
    Positive variance means actual cost is above budget.
    """

    return (
        df.groupby("Project_Name", as_index=False)
        .agg(
            Total_Cost=("Total_Cost", "sum"),
            Budgeted_Cost=("Budgeted_Cost", "sum"),
            Cost_Variance=("Cost_Variance", "sum"),
            Avg_Cost_Variance_Pct=("Cost_Variance_Pct", "mean"),
        )
        .sort_values("Cost_Variance", ascending=False)
        .head(top_n)
    )