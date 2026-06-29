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
from src.ml.anomaly_detection import detect_cost_anomalies
from src.assistant.mock_llm import ask_procurement_assistant

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

# Anomaly Detection
st.subheader("Cost Anomaly Detection")

if len(filtered_df) > 10:
    anomaly_df = detect_cost_anomalies(filtered_df)

    anomaly_count = anomaly_df["Is_Anomaly"].sum()
    anomaly_rate = anomaly_count / len(anomaly_df) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Detected Anomalies", f"{anomaly_count}")
    col2.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
    col3.metric(
        "Highest Unit Cost vs Category Median",
        f"{anomaly_df['Unit_Cost_vs_Category_Median'].max():.2f}x",
    )

    anomaly_records = anomaly_df[anomaly_df["Is_Anomaly"]].copy()

    if not anomaly_records.empty:
        fig_anomaly = px.scatter(
            anomaly_df,
            x="Unit_Cost",
            y="Total_Cost",
            color="Anomaly_Label",
            size="Quantity",
            hover_data=[
                "PO_Number",
                "Project_Name",
                "Supplier_Name",
                "Material_Category",
                "Cost_Variance_Pct",
                "Lead_Time_Days",
            ],
            title="Cost Anomaly Detection: Unit Cost vs Total Cost",
        )

        st.plotly_chart(fig_anomaly, width="stretch")

        st.dataframe(
            anomaly_records[
                [
                    "PO_Number",
                    "Project_Name",
                    "Supplier_Name",
                    "Material_Category",
                    "Unit_Cost",
                    "Total_Cost",
                    "Cost_Variance_Pct",
                    "Lead_Time_Days",
                    "Unit_Cost_vs_Category_Median",
                    "Anomaly_Label",
                ]
            ].head(20),
            width="stretch",
        )
    else:
        st.success("No major cost anomalies detected for the selected filters.")
else:
    st.info("Not enough filtered records to run anomaly detection.")

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
tab1, tab2, tab3, tab4 = st.tabs(
    ["Cost Overruns", "Supplier Scorecard", "Raw Data Preview", "AI Assistant"]
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

with tab4:
    st.subheader("AI Procurement & Cost Assistant")
    st.caption(
        "Ask business questions about suppliers, projects, cost overruns, lead times, anomalies, and trends."
    )

    example_questions = [
        "Which suppliers have the highest spend?",
        "Which projects have the highest procurement cost?",
        "Which projects are above budget?",
        "Which material categories have the longest lead times?",
        "Which suppliers should be monitored?",
        "Show monthly procurement trends.",
        "Find unusual cost increases.",
        "Summarize procurement insights.",
    ]

    selected_example = st.selectbox(
        "Example questions",
        options=[""] + example_questions,
    )

    user_query = st.text_input(
        "Ask a question",
        value=selected_example,
        placeholder="Example: Which suppliers have the highest spend?",
    )

    if st.button("Ask Assistant"):
        if user_query.strip():
            response = ask_procurement_assistant(user_query, filtered_df)
            st.markdown(response)
        else:
            st.warning("Please enter a question.")