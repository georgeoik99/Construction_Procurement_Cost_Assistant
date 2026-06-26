from pathlib import Path

import numpy as np
import pandas as pd


def generate_construction_procurement_data(n_rows: int = 750) -> pd.DataFrame:
    """
    Generate synthetic construction procurement and cost data.
    This dataset is fully artificial and safe for GitHub portfolio use.
    """

    np.random.seed(42)

    projects = [
        "Residential Tower A",
        "Commercial Complex B",
        "Hotel Renovation C",
        "Industrial Warehouse D",
        "Metro Station Upgrade E",
        "Office Building F",
    ]

    site_locations = [
        "Athens",
        "Thessaloniki",
        "Patras",
        "Heraklion",
        "Larissa",
        "Volos",
    ]

    contractors = [
        "Apex Construction Group",
        "Helios Civil Works",
        "Atlas Engineering Contractors",
        "Orion Build Partners",
        "Delta Infrastructure Services",
    ]

    suppliers = [
        "Alpha Cement Supplies",
        "Beta Steel Trading",
        "Gamma Electrical Systems",
        "Delta Plumbing Materials",
        "Omega HVAC Equipment",
        "Atlas Safety Equipment",
        "Nordic Timber Solutions",
        "Helios Logistics Services",
    ]

    material_categories = [
        "Concrete",
        "Steel",
        "Electrical",
        "Plumbing",
        "HVAC",
        "Timber",
        "Safety Equipment",
        "Logistics",
    ]

    material_descriptions = {
        "Concrete": ["Ready-mix concrete", "Cement bags", "Concrete additives"],
        "Steel": ["Rebar steel", "Steel beams", "Metal frames"],
        "Electrical": ["Cable trays", "Electrical panels", "Industrial cables"],
        "Plumbing": ["PVC pipes", "Valves", "Water fittings"],
        "HVAC": ["Air handling units", "Ventilation ducts", "HVAC filters"],
        "Timber": ["Wood panels", "Formwork timber", "Plywood sheets"],
        "Safety Equipment": ["Helmets", "Safety barriers", "Protective gloves"],
        "Logistics": ["Material transport", "Crane service", "Site delivery service"],
    }

    buyers = ["Buyer A", "Buyer B", "Buyer C", "Buyer D"]

    category_price_ranges = {
        "Concrete": (40, 180),
        "Steel": (300, 1200),
        "Electrical": (50, 700),
        "Plumbing": (20, 300),
        "HVAC": (500, 3500),
        "Timber": (30, 250),
        "Safety Equipment": (5, 120),
        "Logistics": (200, 2000),
    }

    start_date = pd.Timestamp("2023-01-01")
    end_date = pd.Timestamp("2024-12-31")

    po_dates = pd.to_datetime(
        np.random.choice(pd.date_range(start_date, end_date), size=n_rows)
    )

    rows = []

    for i in range(n_rows):
        category = np.random.choice(material_categories)
        min_price, max_price = category_price_ranges[category]

        po_date = po_dates[i]
        delivery_days = np.random.randint(5, 90)
        requested_days_before_po = np.random.randint(3, 30)

        quantity = np.random.randint(1, 500)

        base_unit_cost = np.random.uniform(min_price, max_price)

        # Simple synthetic inflation effect over time
        months_from_start = (po_date.year - 2023) * 12 + po_date.month
        inflation_factor = 1 + (months_from_start * np.random.uniform(0.002, 0.008))

        unit_cost = round(base_unit_cost * inflation_factor, 2)
        total_cost = round(quantity * unit_cost, 2)

        budgeted_cost = round(total_cost * np.random.uniform(0.85, 1.15), 2)
        cost_variance = round(total_cost - budgeted_cost, 2)
        cost_variance_pct = round((cost_variance / budgeted_cost) * 100, 2)

        requested_date = po_date - pd.Timedelta(days=requested_days_before_po)
        delivery_date = po_date + pd.Timedelta(days=delivery_days)
        lead_time_days = (delivery_date - requested_date).days

        if cost_variance_pct > 12 or lead_time_days > 95:
            risk_level = "High"
        elif cost_variance_pct > 5 or lead_time_days > 65:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        rows.append(
            {
                "Project_ID": f"PRJ{1000 + np.random.randint(1, 999)}",
                "Project_Name": np.random.choice(projects),
                "Site_Location": np.random.choice(site_locations),
                "Contractor_Name": np.random.choice(contractors),
                "Supplier_Name": np.random.choice(suppliers),
                "Material_Category": category,
                "Material_Description": np.random.choice(material_descriptions[category]),
                "PO_Number": f"PO{200000 + i}",
                "PO_Date": po_date,
                "Requested_Date": requested_date,
                "Delivery_Date": delivery_date,
                "Quantity": quantity,
                "Unit_Cost": unit_cost,
                "Total_Cost": total_cost,
                "Budgeted_Cost": budgeted_cost,
                "Cost_Variance": cost_variance,
                "Cost_Variance_Pct": cost_variance_pct,
                "Currency": "EUR",
                "Lead_Time_Days": lead_time_days,
                "Risk_Level": risk_level,
                "Buyer": np.random.choice(buyers),
            }
        )

    df = pd.DataFrame(rows)

    # Add synthetic cost anomalies
    anomaly_indices = np.random.choice(df.index, size=25, replace=False)
    df.loc[anomaly_indices, "Unit_Cost"] = (df.loc[anomaly_indices, "Unit_Cost"] * 2.2).round(2)
    df.loc[anomaly_indices, "Total_Cost"] = (
        df.loc[anomaly_indices, "Quantity"] * df.loc[anomaly_indices, "Unit_Cost"]
    ).round(2)
    df.loc[anomaly_indices, "Cost_Variance"] = (
        df.loc[anomaly_indices, "Total_Cost"] - df.loc[anomaly_indices, "Budgeted_Cost"]
    ).round(2)
    df.loc[anomaly_indices, "Cost_Variance_Pct"] = (
        df.loc[anomaly_indices, "Cost_Variance"] / df.loc[anomaly_indices, "Budgeted_Cost"] * 100
    ).round(2)
    df.loc[anomaly_indices, "Risk_Level"] = "High"

    return df


def save_sample_data() -> None:
    project_root = Path(__file__).resolve().parents[2]
    output_path = project_root / "data" / "sample" / "construction_procurement_sample.csv"

    df = generate_construction_procurement_data()
    df.to_csv(output_path, index=False)

    print(f"Sample construction procurement dataset created: {output_path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")


if __name__ == "__main__":
    save_sample_data()