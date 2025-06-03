import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load data
df = pd.read_csv('vehicle_service_data.csv')

# Preprocess
df['SERVICE_DATE'] = pd.to_datetime(df['SERVICE_DATE'])
df['Month'] = df['SERVICE_DATE'].dt.month_name()

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/garage.png", width=60)
st.sidebar.header("🔧 Filter Options")
month = st.sidebar.selectbox("📅 Select Month", df['Month'].unique())
filtered_df = df[df['Month'] == month]

# Title
st.markdown("<h1 style='color:#4CAF50;'>🚗 Auto Shop Performance Dashboard</h1>", unsafe_allow_html=True)
st.subheader(f"📊 Monthly Overview: {month}")

# Online Reputation
with st.container():
    st.markdown("### 🌐 Online Reputation Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Google Reviews", value="98", delta="+4")
    col2.metric(label="Avg Star Rating", value="4.1 ★")
    col3.metric(label="Negative Reviews (30 days)", value="1 ⚠️")
    st.markdown("**💬 Top Review Keywords:** `Fast`, `Oil Change`, `Friendly`")

# Customer Retention
with st.container():
    st.markdown("### 👥 Customer Retention Snapshot")
    st.write(f"**Total Customers:** {len(filtered_df)}")
    repeat_customers = filtered_df[filtered_df['REPEAT_CUSTOMER'] == 'Yes']
    st.write(f"**Repeat Customers:** {len(repeat_customers)} ({len(repeat_customers)/len(filtered_df)*100:.1f}%)")
    inactive_count = 72  # placeholder
    st.write(f"**Inactive Customers (6+ months):** {inactive_count}")

# Profitability
with st.container():
    st.markdown("### 💰 Service Profitability Breakdown")

    service_profit = filtered_df.groupby('SERVICE_TYPE').agg(
        Revenue=('Revenue', 'mean'),
        Cost=('Cost', 'mean'),
        Jobs=('SERVICE_TYPE', 'count')
    ).reset_index()

    service_profit['Profit Margin (%)'] = ((service_profit['Revenue'] - service_profit['Cost']) /
                                           service_profit['Revenue'] * 100)

    service_profit['Revenue'] = service_profit['Revenue'].round(2)
    service_profit['Cost'] = service_profit['Cost'].round(2)
    service_profit['Profit Margin (%)'] = service_profit['Profit Margin (%)'].round(1)

    # Sort by Profit Margin
    service_profit = service_profit.sort_values(by='Profit Margin (%)', ascending=False)

    st.dataframe(service_profit, use_container_width=True)

    fig = px.bar(
        service_profit,
        y='SERVICE_TYPE',
        x='Profit Margin (%)',
        orientation='h',
        color='Profit Margin (%)',
        color_continuous_scale='greens',
        title='📈 Profit Margin by Service Type'
    )
    fig.update_layout(height=400, xaxis_title='Profit Margin (%)', yaxis_title='Service Type')
    st.plotly_chart(fig, use_container_width=True)

# Summary
with st.container():
    st.markdown("---")
    st.markdown("### 📝 Summary & Tips")
    st.success("✅ Strong margins on tire rotation and A/C services. Consider raising brake service prices.")
    st.warning("⚠️ Respond to 2-star review from May 18th to avoid SEO hit.")
    st.info("📧 Send a follow-up offer to 72 inactive customers.")

# Footer
st.markdown("---")
st.caption("🚘 Auto Shop MVP - Built by Tim Voelker")

# Optional: Inject some custom CSS
st.markdown("""
<style>
    .css-1d391kg {background-color: #f7f7f7;}
    .block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)
