from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data.cleaning import clean_construction_procurement_data
from src.data.ingestion import load_csv
from src.data.validation import validate_required_columns
from src.analytics.spend_analysis import (
    total_cost_by_supplier,
    total_cost_by_project,
    total_cost_by_material_category,
    cost_overrun_by_project,
)
from src.analytics.trends import monthly_procurement_trends
from src.analytics.supplier_segmentation import supplier_scorecard


st.set_page_config(
    page_title="Construction Procurement & Cost Assistant",
    page_icon="🏗️",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "sample" / "construction_procurement_sample.csv"

    df = load_csv(data_path)
    validate_required_columns(df)

    return clean_construction_procurement_data(df)


df = load_data()

st.title("🏗️ Construction Procurement & Cost Assistant")
st.caption(
    "AI-ready procurement and cost intelligence dashboard for construction projects."
)

# Sidebar filters
st.sidebar.header("Filters")

selected_projects = st.sidebar.multiselect(
    "Project",
    options=sorted(df["Project_Name"].unique()),
    default=sorted(df["Project_Name"].unique()),
)

selected_categories = st.sidebar.multiselect(
    "Material Category",
    options=sorted(df["Material_Category"].unique()),
    default=sorted(df["Material_Category"].unique()),
)

selected_risk = st.sidebar.multiselect(
    "Risk Level",
    options=sorted(df["Risk_Level"].unique()),
    default=sorted(df["Risk_Level"].unique()),
)

filtered_df = df[
    (df["Project_Name"].isin(selected_projects))
    & (df["Material_Category"].isin(selected_categories))
    & (df["Risk_Level"].isin(selected_risk))
]

# KPI cards
total_cost = filtered_df["Total_Cost"].sum()
total_budget = filtered_df["Budgeted_Cost"].sum()
total_variance = filtered_df["Cost_Variance"].sum()
po_count = filtered_df["PO_Number"].nunique()
avg_lead_time = filtered_df["Lead_Time_Days"].mean()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Cost", f"€{total_cost:,.0f}")
col2.metric("Budgeted Cost", f"€{total_budget:,.0f}")
col3.metric("Cost Variance", f"€{total_variance:,.0f}")
col4.metric("PO Count", f"{po_count:,}")
col5.metric("Avg Lead Time", f"{avg_lead_time:.1f} days")

st.divider()

# Charts
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Top Suppliers by Cost")
    supplier_cost = total_cost_by_supplier(filtered_df, top_n=10)

    fig_supplier = px.bar(
        supplier_cost,
        x="Total_Cost",
        y="Supplier_Name",
        orientation="h",
        title="Top 10 Suppliers by Total Cost",
    )
    fig_supplier.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_supplier, width="stretch")

with right_col:
    st.subheader("Top Projects by Cost")
    project_cost = total_cost_by_project(filtered_df, top_n=10)

    fig_project = px.bar(
        project_cost,
        x="Total_Cost",
        y="Project_Name",
        orientation="h",
        title="Top Projects by Total Procurement Cost",
    )
    fig_project.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_project, width="stretch")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Monthly Procurement Trend")
    monthly_trends = monthly_procurement_trends(filtered_df)

    fig_monthly = px.line(
        monthly_trends,
        x="PO_Month",
        y="Total_Cost",
        markers=True,
        title="Monthly Total Cost Trend",
    )
    st.plotly_chart(fig_monthly, width="stretch")

with right_col:
    st.subheader("Cost by Material Category")
    category_cost = total_cost_by_material_category(filtered_df)

    fig_category = px.pie(
        category_cost,
        names="Material_Category",
        values="Total_Cost",
        title="Cost Distribution by Material Category",
    )
    st.plotly_chart(fig_category, width="stretch")

st.divider()

# Tables
tab1, tab2, tab3 = st.tabs(
    ["Cost Overruns", "Supplier Scorecard", "Raw Data Preview"]
)

with tab1:
    st.subheader("Projects with Highest Cost Overruns")
    st.dataframe(
        cost_overrun_by_project(filtered_df, top_n=10),
        width="stretch",
    )

with tab2:
    st.subheader("Supplier Risk Scorecard")
    st.dataframe(
        supplier_scorecard(filtered_df),
        width="stretch",
    )

with tab3:
    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.head(100), width="stretch")