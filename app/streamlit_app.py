from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

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


st.set_page_config(
    page_title="Construction Procurement & Cost Assistant",
    page_icon="🏗️",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }

    [data-testid="stSidebar"] {
        min-width: 250px;
        max-width: 250px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.75rem;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "sample" / "construction_procurement_sample.csv"

    df = load_csv(data_path)
    validate_required_columns(df)

    return clean_construction_procurement_data(df)


def format_compact_currency(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"€{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"€{value / 1_000:.1f}K"
    return f"€{value:,.0f}"


def add_assistant_message(role: str, content: str) -> None:
    st.session_state.assistant_messages.append(
        {
            "role": role,
            "content": content,
        }
    )


def ask_assistant(query: str, data: pd.DataFrame) -> None:
    query = query.strip()

    if not query:
        return

    add_assistant_message("user", query)

    response = ask_procurement_assistant(query, data)
    add_assistant_message("assistant", response)


if "assistant_messages" not in st.session_state:
    st.session_state.assistant_messages = [
        {
            "role": "assistant",
            "content": (
                "Hello — I can help you analyze suppliers, projects, cost overruns, "
                "lead times, anomalies, and procurement trends."
            ),
        }
    ]


df = load_data()

# Sidebar filters - compact mode
st.sidebar.header("Filters")
st.sidebar.caption("Leave empty to include all records.")

project_options = sorted(df["Project_Name"].unique())
category_options = sorted(df["Material_Category"].unique())
risk_options = sorted(df["Risk_Level"].unique())

with st.sidebar.expander("Project filters", expanded=False):
    selected_projects_filter = st.multiselect(
        "Projects",
        options=project_options,
        default=[],
    )

with st.sidebar.expander("Material filters", expanded=False):
    selected_categories_filter = st.multiselect(
        "Material categories",
        options=category_options,
        default=[],
    )

with st.sidebar.expander("Risk filters", expanded=False):
    selected_risk_filter = st.multiselect(
        "Risk levels",
        options=risk_options,
        default=[],
    )

selected_projects = selected_projects_filter or project_options
selected_categories = selected_categories_filter or category_options
selected_risk = selected_risk_filter or risk_options

filtered_df = df[
    (df["Project_Name"].isin(selected_projects))
    & (df["Material_Category"].isin(selected_categories))
    & (df["Risk_Level"].isin(selected_risk))
]

# Main layout
main_col, assistant_col = st.columns([4.0, 1.35], gap="large")

with main_col:
    st.title("🏗️ Construction Procurement & Cost Assistant")
    st.caption(
        "AI-ready procurement and cost intelligence dashboard for construction projects."
    )

    total_cost = filtered_df["Total_Cost"].sum()
    total_budget = filtered_df["Budgeted_Cost"].sum()
    total_variance = filtered_df["Cost_Variance"].sum()
    po_count = filtered_df["PO_Number"].nunique()
    avg_lead_time = filtered_df["Lead_Time_Days"].mean()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Cost", format_compact_currency(total_cost))
    col2.metric("Budgeted Cost", format_compact_currency(total_budget))
    col3.metric("Cost Variance", format_compact_currency(total_variance))
    col4.metric("PO Count", f"{po_count:,}")
    col5.metric("Avg Lead Time", f"{avg_lead_time:.1f} days")

    st.divider()

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
        fig_supplier.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=430,
            margin=dict(l=10, r=10, t=55, b=10),
        )
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
        fig_project.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=430,
            margin=dict(l=10, r=10, t=55, b=10),
        )
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
        fig_monthly.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=55, b=10),
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
        fig_category.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=55, b=10),
        )
        st.plotly_chart(fig_category, width="stretch")

    st.divider()

    st.subheader("Cost Anomaly Detection")

    if len(filtered_df) > 10:
        anomaly_df = detect_cost_anomalies(filtered_df)

        anomaly_count = anomaly_df["Is_Anomaly"].sum()
        anomaly_rate = anomaly_count / len(anomaly_df) * 100

        c1, c2, c3 = st.columns(3)

        c1.metric("Detected Anomalies", f"{anomaly_count}")
        c2.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
        c3.metric(
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
                hover_data=[
                    "PO_Number",
                    "Project_Name",
                    "Supplier_Name",
                    "Material_Category",
                    "Quantity",
                    "Cost_Variance_Pct",
                    "Lead_Time_Days",
                    "Unit_Cost_vs_Category_Median",
                ],
                title="Cost Anomaly Detection: Unit Cost vs Total Cost",
                opacity=0.65,
            )

            fig_anomaly.update_traces(
                marker=dict(
                    size=7,
                    line=dict(width=0.5),
                )
            )

            fig_anomaly.update_layout(
                height=500,
                legend_title_text="Record Type",
                margin=dict(l=10, r=10, t=55, b=10),
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


with assistant_col:
    with st.container(border=True):
        st.markdown("### 🤖 AI Insights Assistant")
        st.caption(
            "Ask questions about suppliers, projects, overruns, delays, trends, and anomalies."
        )

        chat_container = st.container(height=380)

        with chat_container:
            for message in st.session_state.assistant_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        with st.expander("Suggested questions", expanded=False):
            suggested_question = st.selectbox(
                "Choose a question",
                options=[
                    "",
                    "Which suppliers have the highest spend?",
                    "Which projects are above budget?",
                    "Which suppliers should be monitored?",
                    "Find unusual cost increases.",
                    "Summarize procurement insights.",
                ],
                key="suggested_question",
            )

            if st.button("Ask selected question", width="stretch"):
                if suggested_question:
                    ask_assistant(suggested_question, filtered_df)
                    st.rerun()
                else:
                    st.warning("Please select a suggested question.")

        with st.form("assistant_form", clear_on_submit=True):
            custom_query = st.text_area(
                "Ask a question",
                height=90,
                placeholder="Type your question here...",
                label_visibility="collapsed",
            )

            submitted = st.form_submit_button("Ask", width="stretch")

            if submitted:
                if custom_query.strip():
                    ask_assistant(custom_query, filtered_df)
                    st.rerun()
                else:
                    st.warning("Please enter a question.")

        if st.button("Clear Chat", width="stretch"):
            st.session_state.assistant_messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Hello — I can help you analyze suppliers, projects, cost overruns, "
                        "lead times, anomalies, and procurement trends."
                    ),
                }
            ]
            st.rerun()