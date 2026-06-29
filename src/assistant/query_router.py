def route_user_query(query: str) -> str:
    """
    Route a natural language question to a supported analytics intent.
    """

    query = query.lower().strip()

    if any(word in query for word in ["monthly", "trend", "trends", "month"]):
        return "monthly_trends"

    if any(word in query for word in ["anomaly", "unusual", "increase", "outlier"]):
        return "anomalies"

    if any(word in query for word in ["above budget", "over budget", "overrun", "variance"]):
        return "cost_overruns"

    if "supplier" in query and any(word in query for word in ["highest", "top", "spend", "cost"]):
        return "top_suppliers"

    if "project" in query and any(word in query for word in ["highest", "top", "cost", "spend"]):
        return "top_projects"

    if any(word in query for word in ["material", "category", "categories"]):
        return "material_categories"

    if any(word in query for word in ["risk", "monitor", "watch"]):
        return "supplier_risk"

    if any(word in query for word in ["delay", "lead time", "delivery"]):
        return "lead_time"

    if any(word in query for word in ["summary", "summarize", "insights"]):
        return "summary"

    return "unknown"