from pathlib import Path

import pandas as pd


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported by load_csv().")

    return pd.read_csv(file_path)


def load_excel(file_path: str | Path) -> pd.DataFrame:
    """
    Load an Excel file into a pandas DataFrame.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() not in [".xlsx", ".xls"]:
        raise ValueError("Only Excel files are supported by load_excel().")

    return pd.read_excel(file_path)