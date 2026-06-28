import pandas as pd


REQUIRED_COLUMNS = [
    "Project_ID",
    "Project_Name",
    "Site_Location",
    "Contractor_Name",
    "Supplier_Name",
    "Material_Category",
    "Material_Description",
    "PO_Number",
    "PO_Date",
    "Requested_Date",
    "Delivery_Date",
    "Quantity",
    "Unit_Cost",
    "Total_Cost",
    "Budgeted_Cost",
    "Cost_Variance",
    "Cost_Variance_Pct",
    "Currency",
    "Lead_Time_Days",
    "Risk_Level",
    "Buyer",
]


def validate_required_columns(df: pd.DataFrame) -> None:
    """
    Validate that the input dataset contains all required columns.
    """

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")