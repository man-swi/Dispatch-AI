import streamlit as st
import pandas as pd
import requests

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Dispatch AI Control Tower",
    layout="wide"
)

# =====================================================
# TITLE
# =====================================================

st.title("AI Logistics Dispatch Control Tower")

# =====================================================
# FETCH SHIPMENTS
# =====================================================

try:

    shipment_response = requests.get(
        "https://dispatch-ai-production-c286.up.railway.app/shipments"
    )

    shipments = shipment_response.json()

    shipment_df = pd.DataFrame(shipments)

except Exception as e:

    shipment_df = pd.DataFrame()

# =====================================================
# SECTION 1 — ACTIVE SHIPMENTS
# =====================================================

st.header("Active Shipments")

if not shipment_df.empty:

    display_columns = [
        col for col in [
            "shipment_id",
            "driver_name",
            "status",
            "updated_eta",
            "severity"
        ]
        if col in shipment_df.columns
    ]

    st.dataframe(
        shipment_df[display_columns],
        width='stretch'
    )

else:

    st.warning("No shipment data available.")

# =====================================================
# SECTION 2 — OPERATIONAL TIMELINE
# =====================================================

st.header("Operational Timeline")

timeline_data = [
    "2:04 PM → Delay detected",
    "2:05 PM → AI contacted driver",
    "2:06 PM → ETA updated",
    "2:07 PM → Customer notified",
    "2:08 PM → Incident logged"
]

for event in timeline_data:

    st.write(event)

# =====================================================
# SECTION 3 — AI METRICS
# =====================================================

st.header("AI Resolution Metrics")

try:

    analytics_response = requests.get(
        "https://dispatch-ai-production-c286.up.railway.app/incident-analytics"
    )

    analytics = analytics_response.json()

except Exception as e:

    analytics = {
        "total_incidents": 0,
        "high_severity_cases": 0,
        "active_escalations": 0
    }

metric1, metric2, metric3 = st.columns(3)

with metric1:

    st.metric(
        label="Total Incidents",
        value=analytics["total_incidents"]
    )

with metric2:

    st.metric(
        label="High Severity Cases",
        value=analytics["high_severity_cases"]
    )

with metric3:

    st.metric(
        label="Active Escalations",
        value=analytics["active_escalations"]
    )

# =====================================================
# SECTION 4 — LIVE INCIDENT FEED
# =====================================================

st.header("Live Incident Feed")

try:

    incident_response = requests.get(
        "https://dispatch-ai-production-c286.up.railway.app/get-incident-history/SH1024"
    )

    incident_data = incident_response.json()

    history = incident_data.get("history", [])

    if history:

        for incident in reversed(history):

            st.error(
                f"""
Shipment: {incident.get('shipment_id')}

Severity: {incident.get('severity')}

Reason: {incident.get('delay_reason')}

Summary: {incident.get('operational_summary')}
"""
            )

    else:

        st.info("No incidents found.")

except Exception as e:

    st.warning("Unable to fetch incident feed.")

# =====================================================
# SECTION 5 — ROUTE RISK ANALYSIS
# =====================================================

st.header("Route Risk Intelligence")

try:

    route_response = requests.get(
        "https://dispatch-ai-production-c286.up.railway.app/route-risk-analysis"
    )

    route_data = route_response.json()

    route_analysis = route_data.get(
        "route_analysis",
        {}
    )

    if route_analysis:

        route_rows = []

        for route, stats in route_analysis.items():

            route_rows.append({
                "Route": route,
                "Total Incidents": stats["total_incidents"],
                "Critical Cases": stats["critical_cases"],
                "High Severity": stats["high_cases"]
            })

        route_df = pd.DataFrame(route_rows)

        st.dataframe(
            route_df,
            width='stretch'
        )

    else:

        st.info("No route intelligence available.")

except Exception as e:

    st.warning("Unable to fetch route analytics.")

# =====================================================
# SECTION 6 — DRIVER RISK ANALYSIS
# =====================================================

st.header("Driver Risk Monitoring")

try:

    driver_response = requests.get(
        "https://dispatch-ai-production-c286.up.railway.app/driver-risk-analysis"
    )

    driver_data = driver_response.json()

    driver_analysis = driver_data.get(
        "driver_analysis",
        {}
    )

    if driver_analysis:

        driver_rows = []

        for driver, stats in driver_analysis.items():

            driver_rows.append({
                "Driver": driver,
                "Total Incidents": stats["total_incidents"],
                "Critical Cases": stats["critical_cases"],
                "High Severity": stats["high_cases"]
            })

        driver_df = pd.DataFrame(driver_rows)

        st.dataframe(
            driver_df,
            width='stretch'
        )

    else:

        st.info("No driver analytics available.")

except Exception as e:

    st.warning("Unable to fetch driver analytics.")

# =====================================================
# SECTION 7 — OPERATIONAL HOTSPOTS
# =====================================================

st.header("Operational Hotspots")

try:

    hotspot_response = requests.get(
        "https://dispatch-ai-production-c286.up.railway.app/operational-hotspots"
    )

    hotspot_data = hotspot_response.json()

    hotspots = hotspot_data.get(
        "high_risk_routes",
        []
    )

    if hotspots:

        hotspot_rows = []

        for route, count in hotspots:

            hotspot_rows.append({
                "Route": route,
                "Incident Count": count
            })

        hotspot_df = pd.DataFrame(hotspot_rows)

        st.dataframe(
            hotspot_df,
            width='stretch'
        )

    else:

        st.info("No hotspot data available.")

except Exception as e:

    st.warning("Unable to fetch hotspot analytics.")

# =====================================================
# SECTION 8 — REPEAT DRIVER ISSUES
# =====================================================

st.header("Repeat Driver Issue Detection")

try:

    repeat_response = requests.get(
        "https://dispatch-ai-production-c286.up.railway.app/repeat-driver-issues"
    )

    repeat_data = repeat_response.json()

    repeat_drivers = repeat_data.get(
        "repeat_driver_issues",
        {}
    )

    if repeat_drivers:

        repeat_rows = []

        for driver, count in repeat_drivers.items():

            repeat_rows.append({
                "Driver": driver,
                "Repeated Incidents": count
            })

        repeat_df = pd.DataFrame(repeat_rows)

        st.dataframe(
            repeat_df,
            width='stretch'
        )

    else:

        st.success("No repeat driver issues detected.")

except Exception as e:

    st.warning("Unable to fetch repeat driver analytics.")

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "AI Logistics Dispatch Delay Management Platform"
)