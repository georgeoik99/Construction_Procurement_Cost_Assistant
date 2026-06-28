import pandas as pd


DATE_COLUMNS = ["PO_Date", "Requested_Date", "Delivery_Date"]

NUMERIC_COLUMNS = [
    "Quantity",
    "Unit_Cost",
    "Total_Cost",
    "Budgeted_Cost",
    "Cost_Variance",
    "Cost_Variance_Pct",
    "Lead_Time_Days",
]


def clean_construction_procurement_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean construction procurement and cost dataset.
    """

    df = df.copy()

    df = df.drop_duplicates()

    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    text_columns = df.select_dtypes(include="object").columns

    for col in text_columns:
        df[col] = df[col].astype(str).str.strip()

    df["PO_Month"] = df["PO_Date"].dt.to_period("M").astype(str)
    df["PO_Year"] = df["PO_Date"].dt.year

    df = df.dropna(subset=["PO_Date", "Supplier_Name", "Project_Name", "Total_Cost"])

    return df