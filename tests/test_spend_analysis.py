import pandas as pd

from src.analytics.spend_analysis import (
    total_cost_by_supplier,
    total_cost_by_project,
    total_cost_by_material_category,
    cost_overrun_by_project,
)


def sample_dataframe():
    return pd.DataFrame(
        {
            "Supplier_Name": ["Supplier A", "Supplier A", "Supplier B"],
            "Project_Name": ["Project X", "Project Y", "Project X"],
            "Material_Category": ["Steel", "Concrete", "Steel"],
            "PO_Number": ["PO1", "PO2", "PO3"],
            "Total_Cost": [1000, 2000, 4000],
            "Unit_Cost": [10, 20, 40],
            "Budgeted_Cost": [900, 2500, 2800],
            "Cost_Variance": [100, -500, 1200],
            "Cost_Variance_Pct": [11.1, -20.0, 42.8],
            "Lead_Time_Days": [30, 45, 60],
        }
    )


def test_total_cost_by_supplier():
    df = sample_dataframe()
    result = total_cost_by_supplier(df)

    assert len(result) == 2
    assert result.iloc[0]["Supplier_Name"] == "Supplier B"
    assert result.iloc[0]["Total_Cost"] == 4000
    assert "PO_Count" in result.columns
    assert "Avg_Unit_Cost" in result.columns


def test_total_cost_by_project():
    df = sample_dataframe()
    result = total_cost_by_project(df)

    assert len(result) == 2
    assert result.iloc[0]["Project_Name"] == "Project X"
    assert result.iloc[0]["Total_Cost"] == 5000
    assert "Avg_Cost_Variance_Pct" in result.columns


def test_total_cost_by_material_category():
    df = sample_dataframe()
    result = total_cost_by_material_category(df)

    assert len(result) == 2
    assert result.iloc[0]["Material_Category"] == "Steel"
    assert result.iloc[0]["Total_Cost"] == 5000
    assert "Avg_Lead_Time_Days" in result.columns


def test_cost_overrun_by_project():
    df = sample_dataframe()
    result = cost_overrun_by_project(df)

    assert len(result) == 2
    assert result.iloc[0]["Project_Name"] == "Project X"
    assert result.iloc[0]["Cost_Variance"] == 1300
    assert "Budgeted_Cost" in result.columns