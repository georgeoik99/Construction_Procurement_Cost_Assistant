import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.analytics.spend_analysis import (
    cost_overrun_by_project,
    total_cost_by_material_category,
    total_cost_by_project,
    total_cost_by_supplier,
)
from src.analytics.supplier_segmentation import supplier_scorecard
from src.analytics.trends import monthly_procurement_trends
from src.assistant.mock_llm import ask_procurement_assistant
from src.data.cleaning import clean_construction_procurement_data
from src.data.ingestion import load_csv
from src.data.validation import validate_required_columns
from src.ml.anomaly_detection import detect_cost_anomalies


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FRONTEND_PATH = PROJECT_ROOT / "frontend"
TEMPLATES_PATH = FRONTEND_PATH / "templates"
STATIC_PATH = FRONTEND_PATH / "static"

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "construction_procurement_sample.csv"
)


app = FastAPI(
    title="Construction Procurement & Cost Assistant API",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_PATH),
    name="static",
)


templates = Jinja2Templates(
    directory=TEMPLATES_PATH
)


class AssistantFilters(BaseModel):
    project: str | None = None
    category: str | None = None
    risk_level: str | None = None


class AssistantRequest(BaseModel):
    query: str
    filters: AssistantFilters | None = None


def load_procurement_data() -> pd.DataFrame:
    """
    Load, validate and clean the construction procurement dataset.
    """

    df = load_csv(DATA_PATH)

    validate_required_columns(df)

    return clean_construction_procurement_data(df)


def filter_dataframe(
    df: pd.DataFrame,
    project: str | None = None,
    category: str | None = None,
    risk_level: str | None = None,
) -> pd.DataFrame:
    """
    Apply optional dashboard filters.
    """

    filtered_df = df.copy()

    if project:
        filtered_df = filtered_df[
            filtered_df["Project_Name"] == project
        ]

    if category:
        filtered_df = filtered_df[
            filtered_df["Material_Category"] == category
        ]

    if risk_level:
        filtered_df = filtered_df[
            filtered_df["Risk_Level"] == risk_level
        ]

    return filtered_df


def dataframe_records(
    df: pd.DataFrame,
) -> list[dict]:
    """
    Convert a DataFrame into JSON-safe records.
    """

    return json.loads(
        df.to_json(
            orient="records",
            date_format="iso",
        )
    )


def empty_dashboard_response() -> dict:
    """
    Return an empty dashboard response.
    """

    return {
        "kpis": {
            "total_cost": 0.0,
            "budgeted_cost": 0.0,
            "cost_variance": 0.0,
            "po_count": 0,
            "avg_lead_time": 0.0,
        },
        "suppliers": [],
        "projects": [],
        "monthly_trends": [],
        "categories": [],
        "anomalies": [],
        "anomaly_summary": {
            "count": 0,
            "rate": 0.0,
            "highest_cost_ratio": 0.0,
        },
        "cost_overruns": [],
        "supplier_scorecard": [],
        "raw_preview": [],
    }


@app.get("/")
def home(request: Request):
    """
    Render the HTML frontend.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/api/filters")
def get_filters():
    """
    Return filter options for the frontend.
    """

    df = load_procurement_data()

    return {
        "projects": sorted(
            df["Project_Name"]
            .dropna()
            .unique()
            .tolist()
        ),
        "categories": sorted(
            df["Material_Category"]
            .dropna()
            .unique()
            .tolist()
        ),
        "risk_levels": sorted(
            df["Risk_Level"]
            .dropna()
            .unique()
            .tolist()
        ),
    }


@app.get("/api/dashboard")
def get_dashboard(
    project: str | None = Query(default=None),
    category: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
):
    """
    Return dashboard analytics, anomaly detection results,
    and operational data tables.
    """

    df = load_procurement_data()

    filtered_df = filter_dataframe(
        df=df,
        project=project,
        category=category,
        risk_level=risk_level,
    )

    if filtered_df.empty:
        return empty_dashboard_response()

    supplier_data = total_cost_by_supplier(
        filtered_df,
        top_n=10,
    )

    project_data = total_cost_by_project(
        filtered_df,
        top_n=10,
    )

    monthly_data = monthly_procurement_trends(
        filtered_df
    )

    category_data = total_cost_by_material_category(
        filtered_df
    )

    cost_overrun_data = cost_overrun_by_project(
        filtered_df,
        top_n=10,
    )

    supplier_scorecard_data = supplier_scorecard(
        filtered_df
    )

    raw_preview_data = (
        filtered_df
        .sort_values(
            "PO_Date",
            ascending=False,
        )
        .head(100)
    )

    if len(filtered_df) > 10:
        anomaly_df = detect_cost_anomalies(
            filtered_df
        )

        anomaly_count = int(
            anomaly_df["Is_Anomaly"].sum()
        )

        anomaly_rate = (
            anomaly_count
            / len(anomaly_df)
            * 100
        )

        highest_cost_ratio = float(
            anomaly_df[
                "Unit_Cost_vs_Category_Median"
            ].max()
        )

    else:
        anomaly_df = filtered_df.copy()

        anomaly_df["Is_Anomaly"] = False
        anomaly_df["Anomaly_Label"] = "Normal"
        anomaly_df[
            "Unit_Cost_vs_Category_Median"
        ] = 0.0

        anomaly_count = 0
        anomaly_rate = 0.0
        highest_cost_ratio = 0.0

    return {
        "kpis": {
            "total_cost": float(
                filtered_df["Total_Cost"].sum()
            ),
            "budgeted_cost": float(
                filtered_df["Budgeted_Cost"].sum()
            ),
            "cost_variance": float(
                filtered_df["Cost_Variance"].sum()
            ),
            "po_count": int(
                filtered_df["PO_Number"].nunique()
            ),
            "avg_lead_time": float(
                filtered_df["Lead_Time_Days"].mean()
            ),
        },
        "suppliers": dataframe_records(
            supplier_data
        ),
        "projects": dataframe_records(
            project_data
        ),
        "monthly_trends": dataframe_records(
            monthly_data
        ),
        "categories": dataframe_records(
            category_data
        ),
        "anomalies": dataframe_records(
            anomaly_df
        ),
        "anomaly_summary": {
            "count": anomaly_count,
            "rate": anomaly_rate,
            "highest_cost_ratio": highest_cost_ratio,
        },
        "cost_overruns": dataframe_records(
            cost_overrun_data
        ),
        "supplier_scorecard": dataframe_records(
            supplier_scorecard_data
        ),
        "raw_preview": dataframe_records(
            raw_preview_data
        ),
    }


@app.post("/api/assistant")
def assistant(
    request_data: AssistantRequest,
):
    """
    Answer procurement and cost analytics questions.
    """

    df = load_procurement_data()

    filters = (
        request_data.filters
        or AssistantFilters()
    )

    filtered_df = filter_dataframe(
        df=df,
        project=filters.project,
        category=filters.category,
        risk_level=filters.risk_level,
    )

    response = ask_procurement_assistant(
        request_data.query,
        filtered_df,
    )

    return {
        "response": response,
    }


@app.get("/api/health")
def health_check():
    """
    API health endpoint.
    """

    return {
        "status": "healthy",
        "service": (
            "Construction Procurement "
            "& Cost Assistant"
        ),
    }