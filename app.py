"""
Commercial Fleet & Last-Mile Delivery Cost-Per-Mile (CPM) Audit Suite (v2.0)
US DOT Fleet Unit Economics, Fuel-Card MPG Variance Audit, PM Service Alerts & Excel Export
"""

import io
from datetime import datetime, timezone
import streamlit as st
import pandas as pd
import plotly.express as px
from fleet_audit_engine import DEFAULT_FLEET, audit_delivery_fleet

st.set_page_config(page_title="Commercial Fleet & Delivery CPM Audit Suite", page_icon="🚚", layout="wide")
st.title("🚚 Commercial Fleet & Last-Mile Delivery Cost-Per-Mile (CPM) Audit Suite")
st.caption("Cost Per Mile (CPM) vs. Revenue Per Mile (RPM) • Fuel-Card MPG Variance & Theft Audit • Preventive Maintenance Alerts • Excel Export")
st.divider()

uploaded = st.sidebar.file_uploader("Upload Custom Fleet Trip & Fuel Ledger (.csv or .xlsx)", type=["csv", "xlsx"])
base_df = (pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)) if uploaded else pd.DataFrame(DEFAULT_FLEET)

st.subheader("Interactive Fleet Vehicle Trip, Fuel & Maintenance Ledger")
st.caption("Edit miles driven, fuel gallons, repair spend, or freight revenue below to recalculate Cost Per Mile and fuel efficiency alerts.")
edited_df = st.data_editor(base_df, width="stretch", num_rows="dynamic")

res = audit_delivery_fleet(edited_df)
out_df = res["df"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Fleet Cost Per Mile (CPM)", f"${res['fleet_cpm']:.3f} / mi", delta=f"Revenue/Mi: ${res['fleet_rpm']:.3f}")
c2.metric("Total Fleet Net Profit", f"${res['total_profit']:,.2f}", delta=f"Across {res['total_miles']:,} Miles")
c3.metric("Fuel / MPG Anomaly Alerts", f"{res['fuel_anomalies']}", delta="Fuel Card & Idling Audit")
c4.metric("PM Service Due (<=1,500 mi)", f"{res['pm_due_count']}", delta="DOT Safety & Oil Countdown")

tab1, tab2, tab3 = st.tabs(["📋 Vehicle CPM & Fuel Audit Table", "📈 Cost vs. Revenue Per Mile Charts", "📥 3-Sheet Excel Fleet Audit Workbook"])

with tab1:
    st.dataframe(out_df[["Unit_ID", "Vehicle_Type", "Route_Corridor", "Miles_Driven", "Actual_MPG", "MPG_Variance_Pct", "Fuel_Audit_Status", "Cost_Per_Mile_USD", "Revenue_Per_Mile_USD", "Net_Profit_USD", "PM_Service_Alert"]], width="stretch")

with tab2:
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.bar(out_df, x="Unit_ID", y=["Cost_Per_Mile_USD", "Revenue_Per_Mile_USD"], barmode="group", title="Cost Per Mile vs. Revenue Per Mile ($/mi)"), width="stretch")
    col2.plotly_chart(px.bar(out_df, x="Unit_ID", y="Net_Profit_USD", color="Fuel_Audit_Status", title="Net Vehicle Contribution & Fuel Efficiency Status ($)"), width="stretch")

with tab3:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        pd.DataFrame([
            {"Fleet_Metric": "Audit Timestamp (UTC)", "Value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")},
            {"Fleet_Metric": "Total Fleet Miles Audited", "Value": f"{res['total_miles']:,} mi"},
            {"Fleet_Metric": "Weighted Fleet Cost Per Mile ($)", "Value": f"${res['fleet_cpm']:.3f}"},
            {"Fleet_Metric": "Weighted Fleet Revenue Per Mile ($)", "Value": f"${res['fleet_rpm']:.3f}"},
            {"Fleet_Metric": "Total Fleet Operating Profit ($)", "Value": f"${res['total_profit']:,.2f}"},
            {"Fleet_Metric": "Fuel / MPG Anomaly Flags", "Value": res["fuel_anomalies"]},
            {"Fleet_Metric": "Vehicles Due for PM Service", "Value": res["pm_due_count"]},
        ]).to_excel(writer, sheet_name="01_Fleet_Executive_Summary", index=False)
        out_df.to_excel(writer, sheet_name="02_Vehicle_CPM_Audit", index=False)

    st.download_button("📊 Download 3-Sheet Fleet CPM Audit Workbook (.xlsx)", buf.getvalue(), "Commercial_Fleet_CPM_Audit_Suite.xlsx")
