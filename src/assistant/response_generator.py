import pandas as pd

from src.analytics.spend_analysis import (
    total_cost_by_supplier,
    total_cost_by_project,
    total_cost_by_material_category,
    cost_overrun_by_project,
)
from src.analytics.supplier_segmentation import supplier_scorecard
from src.analytics.trends import monthly_procurement_trends
from src.ml.anomaly_detection import detect_cost_anomalies
from src.assistant.query_router import route_user_query


def format_currency(value: float) -> str:
    return f"€{value:,.0f}"


def generate_assistant_response(query: str, df: pd.DataFrame) -> str:
    """
    Generate a business-friendly response based on the user's natural language query.
    """

    intent = route_user_query(query)

    if df.empty:
        return "No data available for the selected filters."

    if intent == "top_suppliers":
        result = total_cost_by_supplier(df, top_n=5)

        lines = ["### Top suppliers by total cost"]
        for _, row in result.iterrows():
            lines.append(
                f"- **{row['Supplier_Name']}**: {format_currency(row['Total_Cost'])} "
                f"across {int(row['PO_Count'])} POs"
            )

        return "\n".join(lines)

    if intent == "top_projects":
        result = total_cost_by_project(df, top_n=5)

        lines = ["### Top projects by procurement cost"]
        for _, row in result.iterrows():
            lines.append(
                f"- **{row['Project_Name']}**: {format_currency(row['Total_Cost'])} "
                f"across {int(row['PO_Count'])} POs"
            )

        return "\n".join(lines)

    if intent == "cost_overruns":
        result = cost_overrun_by_project(df, top_n=5)
        result = result[result["Cost_Variance"] > 0]

        if result.empty:
            return "No major cost overruns were found in the selected data."

        lines = ["### Projects with the highest cost overruns"]
        for _, row in result.iterrows():
            lines.append(
                f"- **{row['Project_Name']}**: {format_currency(row['Cost_Variance'])} "
                f"above budget"
            )

        return "\n".join(lines)

    if intent == "material_categories":
        result = total_cost_by_material_category(df).head(5)

        lines = ["### Highest-cost material categories"]
        for _, row in result.iterrows():
            lines.append(
                f"- **{row['Material_Category']}**: {format_currency(row['Total_Cost'])} "
                f"with average lead time {row['Avg_Lead_Time_Days']:.1f} days"
            )

        return "\n".join(lines)

    if intent == "monthly_trends":
        result = monthly_procurement_trends(df)

        peak_month = result.loc[result["Total_Cost"].idxmax()]
        latest_month = result.iloc[-1]

        return (
            "### Monthly procurement trend summary\n"
            f"- Peak month: **{peak_month['PO_Month']}** with "
            f"{format_currency(peak_month['Total_Cost'])}\n"
            f"- Latest month: **{latest_month['PO_Month']}** with "
            f"{format_currency(latest_month['Total_Cost'])}\n"
            f"- Average lead time in latest month: "
            f"**{latest_month['Avg_Lead_Time_Days']:.1f} days**"
        )

    if intent == "supplier_risk":
        result = supplier_scorecard(df)
        risky = result[result["Risk_Flag"].isin(["High", "Medium"])].head(5)

        if risky.empty:
            return "No high or medium supplier risk was detected."

        lines = ["### Suppliers that should be monitored"]
        for _, row in risky.iterrows():
            lines.append(
                f"- **{row['Supplier_Name']}**: {row['Risk_Flag']} risk, "
                f"{int(row['High_Risk_Orders'])} high-risk orders, "
                f"avg lead time {row['Avg_Lead_Time_Days']:.1f} days"
            )

        return "\n".join(lines)

    if intent == "lead_time":
        result = (
            df.groupby("Material_Category", as_index=False)
            .agg(
                Avg_Lead_Time_Days=("Lead_Time_Days", "mean"),
                PO_Count=("PO_Number", "nunique"),
            )
            .sort_values("Avg_Lead_Time_Days", ascending=False)
            .head(5)
        )

        lines = ["### Categories with the longest lead times"]
        for _, row in result.iterrows():
            lines.append(
                f"- **{row['Material_Category']}**: "
                f"{row['Avg_Lead_Time_Days']:.1f} days on average "
                f"across {int(row['PO_Count'])} POs"
            )

        return "\n".join(lines)

    if intent == "anomalies":
        result = detect_cost_anomalies(df)
        anomalies = result[result["Is_Anomaly"]].head(5)

        if anomalies.empty:
            return "No unusual cost records were detected."

        lines = ["### Unusual cost records detected"]
        for _, row in anomalies.iterrows():
            lines.append(
                f"- **{row['PO_Number']}** | {row['Material_Category']} | "
                f"{row['Supplier_Name']} | Unit cost: {format_currency(row['Unit_Cost'])} | "
                f"{row['Unit_Cost_vs_Category_Median']}x category median"
            )

        return "\n".join(lines)

    if intent == "summary":
        total_cost = df["Total_Cost"].sum()
        po_count = df["PO_Number"].nunique()
        top_supplier = total_cost_by_supplier(df, top_n=1).iloc[0]
        top_project = total_cost_by_project(df, top_n=1).iloc[0]
        high_risk_count = (df["Risk_Level"] == "High").sum()

        return (
            "### Procurement and cost summary\n"
            f"- Total procurement cost: **{format_currency(total_cost)}**\n"
            f"- Total PO count: **{po_count}**\n"
            f"- Top supplier: **{top_supplier['Supplier_Name']}** "
            f"with {format_currency(top_supplier['Total_Cost'])}\n"
            f"- Top project: **{top_project['Project_Name']}** "
            f"with {format_currency(top_project['Total_Cost'])}\n"
            f"- High-risk records: **{high_risk_count}**"
        )

    return (
        "I can answer questions about suppliers, projects, cost overruns, "
        "material categories, monthly trends, lead times, anomalies, and summaries."
    )