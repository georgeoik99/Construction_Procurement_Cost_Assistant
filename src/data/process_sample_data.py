from pathlib import Path

from src.data.cleaning import clean_construction_procurement_data
from src.data.ingestion import load_csv
from src.data.validation import validate_required_columns


def process_sample_dataset() -> None:
    project_root = Path(__file__).resolve().parents[2]

    input_path = project_root / "data" / "sample" / "construction_procurement_sample.csv"
    output_path = project_root / "data" / "processed" / "construction_procurement_clean.csv"

    df = load_csv(input_path)
    validate_required_columns(df)

    clean_df = clean_construction_procurement_data(df)
    clean_df.to_csv(output_path, index=False)

    print(f"Processed dataset saved: {output_path}")
    print(f"Rows: {len(clean_df)}")
    print(f"Columns: {len(clean_df.columns)}")


if __name__ == "__main__":
    process_sample_dataset()