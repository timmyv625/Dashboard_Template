import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load and preprocess data
df = pd.read_csv('vehicle_service_data.csv')
df['SERVICE_DATE'] = pd.to_datetime(df['SERVICE_DATE'])
df['Month'] = df['SERVICE_DATE'].dt.month_name()

# Sidebar filters
st.sidebar.header("Filter Options")
month = st.sidebar.selectbox("Select Month", df['Month'].unique())
filtered_df = df[df['Month'] == month]

# --- Custom CSS for center titles and modern feel ---
st.markdown("""
    <style>
    .centered-title {
        text-align: center;
        font-size: 2.3em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    .section-header {
        font-size: 1.4em;
        font-weight: 600;
        border-bottom: 1px solid #ddd;
        margin-top: 30px;
        margin-bottom: 10px;
        padding-bottom: 5px;
        color: #34495e;
    }
    .metric-box {
        padding: 10px;
        background-color: #f9f9f9;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<div class='centered-title'>Auto Shop Performance Dashboard</div>", unsafe_allow_html=True)
st.write(f"**Month Selected:** {month}")

# --- Section 1: Online Reputation ---
st.markdown("<div class='section-header'>Online Reputation Summary</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Total Google Reviews", "98", "+4")
col2.metric("Avg Star Rating", "4.1")
col3.metric("Neg. Reviews (30d)", "1")

st.markdown("Top Review Keywords: _Fast_, _Oil Change_, _Friendly_")

# --- Section 2: Customer Retention ---
st.markdown("<div class='section-header'>Customer Retention Snapshot</div>", unsafe_allow_html=True)

total_customers = len(filtered_df)
repeat_customers = filtered_df[filtered_df['REPEAT_CUSTOMER'] == 'Yes']
inactive_count = 72  # placeholder

st.write(f"**Total Customers:** {total_customers}")
st.write(f"**Repeat Customers:** {len(repeat_customers)} ({len(repeat_customers)/total_customers*100:.1f}%)")
st.write(f"**Inactive Customers (6+ months):** {inactive_count}")

# --- Section 3: Profitability ---
st.markdown("<div class='section-header'>Service Profitability Breakdown</div>", unsafe_allow_html=True)

service_profit = filtered_df.groupby('SERVICE_TYPE').agg(
    Revenue=('Revenue', 'mean'),
    Cost=('Cost', 'mean'),
    Jobs=('SERVICE_TYPE', 'count')
).reset_index()

service_profit['Profit Margin (%)'] = (
    (service_profit['Revenue'] - service_profit['Cost']) / service_profit['Revenue'] * 100
).round(1)

service_profit = service_profit.sort_values(by='Profit Margin (%)', ascending=False)

st.dataframe(service_profit, use_container_width=True)

# Interactive Plotly chart
fig = px.bar(
    service_profit,
    x='Profit Margin (%)',
    y='SERVICE_TYPE',
    orientation='h',
    color='Profit Margin (%)',
    color_continuous_scale='Tealgrn'
)
fig.update_layout(
    height=400,
    xaxis_title="Profit Margin (%)",
    yaxis_title="Service Type",
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=10, r=10, t=40, b=10),
)
st.plotly_chart(fig, use_container_width=True)

# --- Summary Section ---
st.markdown("<div class='section-header'>Summary & Recommendations</div>", unsafe_allow_html=True)

st.markdown("- Strong margins on tire rotation and A/C services.")
st.markdown("- Consider raising prices for brake services.")
st.markdown("- Respond to 2-star review from May 18 to maintain SEO.")
st.markdown("- Send follow-up offer to inactive customers.")

# --- Footer ---
st.markdown("---")
st.caption("Auto Shop MVP — Built by Tim Voelker")
