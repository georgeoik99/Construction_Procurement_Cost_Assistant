import pandas as pd

from src.assistant.query_router import route_user_query
from src.assistant.mock_llm import ask_procurement_assistant


def sample_dataframe():
    return pd.DataFrame(
        {
            "Supplier_Name": ["Supplier A", "Supplier B", "Supplier A"],
            "Project_Name": ["Project X", "Project Y", "Project X"],
            "Material_Category": ["Steel", "Concrete", "Steel"],
            "PO_Number": ["PO1", "PO2", "PO3"],
            "PO_Month": ["2024-01", "2024-01", "2024-02"],
            "Quantity": [10, 20, 15],
            "Unit_Cost": [100, 200, 150],
            "Total_Cost": [1000, 4000, 2250],
            "Budgeted_Cost": [900, 3500, 2000],
            "Cost_Variance": [100, 500, 250],
            "Cost_Variance_Pct": [11.1, 14.3, 12.5],
            "Lead_Time_Days": [30, 70, 45],
            "Risk_Level": ["Low", "High", "Medium"],
        }
    )


def test_route_top_suppliers_query():
    query = "Which suppliers have the highest spend?"
    assert route_user_query(query) == "top_suppliers"


def test_route_cost_overruns_query():
    query = "Which projects are above budget?"
    assert route_user_query(query) == "cost_overruns"


def test_assistant_returns_supplier_response():
    df = sample_dataframe()
    response = ask_procurement_assistant(
        "Which suppliers have the highest spend?",
        df,
    )

    assert "Top suppliers" in response
    assert "Supplier B" in response


def test_assistant_returns_summary_response():
    df = sample_dataframe()
    response = ask_procurement_assistant(
        "Summarize procurement insights",
        df,
    )

    assert "summary" in response.lower()
    assert "Total procurement cost" in response