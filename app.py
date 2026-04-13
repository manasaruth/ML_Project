import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Predictive Maintenance Dashboard 🚀")

# ----------------------------
# Load CSV
# ----------------------------
df = pd.read_csv("updated_data_final.csv")
df['Datetime'] = pd.to_datetime(df['Datetime'])

# Ensure numeric columns for KPIs
for col in ['Early_Warning_Hours', 'Avoided_Downtime_Hours']:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors='coerce')

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")
machine_id = st.sidebar.selectbox("Choose Machine ID", df['Machine_ID'].unique())
operation_modes = df['Operation_Mode'].unique()
selected_modes = st.sidebar.multiselect("Filter by Operation Mode", operation_modes, default=list(operation_modes))
min_date = df['Datetime'].min()
max_date = df['Datetime'].max()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])
risk_levels = ["Low", "Medium", "High"]
selected_risks = st.sidebar.multiselect("Select Risk Levels", risk_levels, default=risk_levels)

# Apply filters
filtered_df = df[
    (df['Machine_ID'] == machine_id) &
    (df['Operation_Mode'].isin(selected_modes)) &
    (df['Datetime'].dt.date >= start_date) &
    (df['Datetime'].dt.date <= end_date) &
    (df['Risk_Level'].isin(selected_risks))
]

# ----------------------------
# Predictive Maintenance Overview
# ----------------------------
st.subheader("Predictive Maintenance Overview")

risk_counts = filtered_df['Risk_Level'].value_counts().reindex(risk_levels, fill_value=0)
colors = {'Low':'green','Medium':'orange','High':'red'}

fig, ax = plt.subplots()
bars = ax.bar(risk_counts.index, risk_counts.values, color=[colors[i] for i in risk_counts.index])
ax.set_title("Risk Distribution")
ax.set_xlabel("Risk Level")
ax.set_ylabel("Count")
st.pyplot(fig)

st.metric("High-Risk Assets", risk_counts['High'])

# ----------------------------
# Machine Anomaly Dashboard
# ----------------------------
st.subheader("Machine Anomaly Dashboard")

fig, ax = plt.subplots(figsize=(10,4))
for r_level, color in colors.items():
    temp = filtered_df[filtered_df['Risk_Level'] == r_level]
    ax.plot(temp['Datetime'], temp['Anomaly_Score'], marker='o', linestyle='-', color=color, label=r_level)
ax.set_xlabel("Datetime")
ax.set_ylabel("Anomaly Score")
ax.set_title("Anomaly Score Trend by Risk Level")
ax.legend()
st.pyplot(fig)

# Sensor Deviations
st.write("### Sensor Deviations")
sensor_cols = ['Temp_Deviation', 'Vibration_Power_Ratio', 'Error_Rolling']
for sensor in sensor_cols:
    if sensor in filtered_df.columns:
        st.line_chart(filtered_df.set_index('Datetime')[sensor])

# ----------------------------
# Maintenance Alert Panel
# ----------------------------
st.subheader("High Risk Alerts 🚨")
high_risk = filtered_df[filtered_df['Risk_Level'] == 'High']
st.dataframe(high_risk.style.highlight_max(subset=['Anomaly_Score'], color='red'))

st.write("### Recommended Inspection Priority")
st.write(high_risk.sort_values(by='Anomaly_Score', ascending=False))

# ----------------------------
# Historical Risk Analysis
# ----------------------------
st.subheader("Historical Risk Analysis")
st.write("### Risk Escalation Timeline")
st.line_chart(filtered_df.set_index('Datetime')['Anomaly_Score'])

st.write("### Last 5 Days Sensor Behavior")
st.line_chart(filtered_df.set_index('Datetime')[sensor_cols].tail(5))

# ----------------------------
# KPIs Panel
# ----------------------------
st.subheader("Key Performance Indicators (KPIs)")

if not filtered_df.empty:
    kpi_df = filtered_df
else:
    st.warning("⚠️ No data for selected filters. Showing overall dataset stats.")
    kpi_df = df  # fallback to full dataset

st.metric("Average Early Warning Hours", round(kpi_df['Early_Warning_Hours'].mean(), 2))
st.metric("Total Avoided Downtime (Hours)", kpi_df['Avoided_Downtime_Hours'].sum())

# ----------------------------
# 🤖 AI Maintenance Agent
# ----------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Maintenance Agent")

# Safe risk handling
selected_risk_level = "Low"
if not filtered_df.empty:
    selected_risk_level = filtered_df['Risk_Level'].iloc[-1]

if st.sidebar.button("🔍 Generate Action Plan"):

    st.write("✅ Button clicked")  # Debug

    st.subheader(f"🛠️ AI Maintenance Plan for {machine_id}")
    st.write(f"Machine ID: {machine_id}")
    st.info(f"Detected Risk Level: {selected_risk_level}")

    with st.spinner("Analyzing machine condition..."):

        if selected_risk_level == "High":
            st.error("🚨 High Risk Detected!")
            st.write("Reduce load, inspect bearings, alert team")

        elif selected_risk_level == "Medium":
            st.warning("⚠️ Medium Risk Detected")
            st.write("Monitor closely, schedule maintenance")

        else:
            st.success("✅ Low Risk")
            st.write("Continue normal operation")