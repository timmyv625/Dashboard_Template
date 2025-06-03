import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data (placeholder: you would replace this with the real dataset)
df = pd.read_csv('vehicle_service_data.csv')  # Example file name

# Sidebar filters

df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.month_name()

st.sidebar.header("Filter Options")
month = st.sidebar.selectbox("Select Month", df['Month'].unique())
filtered_df = df[df['Month'] == month]

# Title
st.title("Auto Shop Performance Dashboard")
st.subheader(f"Monthly Overview: {month}")

# 1. Online Reputation Summary (Mocked)
st.markdown("### Online Reputation Summary")
st.metric(label="Total Google Reviews", value="198", delta="+4")
st.metric(label="Avg Star Rating", value="4.3 ★")
st.metric(label="Negative Reviews (last 30 days)", value="1 ⚠️")
st.markdown("**Top Review Keywords:** Fast, Oil Change, Friendly")

# 2. Customer Retention Snapshot
st.markdown("### Customer Retention Snapshot")
st.write("**Total Customers:**", len(filtered_df))
repeat_customers = filtered_df[filtered_df['REPEAT_CUSTOMER'] == 'Yes']
st.write("**Repeat Customers:**", len(repeat_customers), f"({len(repeat_customers)/len(filtered_df)*100:.1f}%)")

inactive_count = 72  # placeholder
st.write("**Inactive Customers (6+ months):**", inactive_count)

# 3. Service Profitability
st.markdown("### Service Profitability Breakdown")
service_profit = filtered_df.groupby('SERVICE_TYPE').agg({
    'Revenue': 'mean',
    'Cost': 'mean',
    'SERVICE_TYPE': 'count'
}).rename(columns={'SERVICE_TYPE': 'Jobs'})
service_profit['Profit Margin (%)'] = ((service_profit['Revenue'] - service_profit['Cost']) / service_profit['Revenue'] * 100).round(1)
st.dataframe(service_profit)

# Visualization
st.markdown("### Revenue vs. Cost per Service")
fig, ax = plt.subplots()
service_profit[['Revenue', 'Cost']].plot(kind='bar', ax=ax)
st.pyplot(fig)

# Summary Box
st.markdown("---")
st.markdown("### Summary & Tips")
st.success("Strong margins on tire rotation and A/C services. Consider raising brake service prices.")
st.warning("Respond to 2-star review from May 18th to avoid SEO hit.")
st.info("Send a follow-up offer to 72 inactive customers.")

# Footer
st.markdown("---")
st.caption("Auto Shop MVP - Built by Tim Voelker")
