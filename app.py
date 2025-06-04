import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
from fpdf import FPDF
import base64
from io import BytesIO

# Load and preprocess data
df = pd.read_csv('vehicle_service_data.csv')

df['SERVICE_DATE'] = pd.to_datetime(df['SERVICE_DATE'], errors='coerce')
df['Month_Num'] = df['SERVICE_DATE'].dt.month
df['Month'] = df['SERVICE_DATE'].dt.month_name()
month_order = list(calendar.month_name)[1:]  # ['January', ..., 'December']
df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)

# Sidebar filter
st.sidebar.header("Filter Options")
month = st.sidebar.selectbox("Select Month", sorted(df['Month'].dropna().unique(), key=lambda x: month_order.index(x)))
filtered_df = df[df['Month'] == month]

# --- CSS ---
st.markdown("""
    <style>
.centered-title {
    text-align: center;
    font-size: 2.3em;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
    color: #e0e0e0;
}
.section-header {
    font-size: 1.4em;
    font-weight: 600;
    border-bottom: 1px solid #444;
    margin-top: 30px;
    margin-bottom: 10px;
    padding-bottom: 5px;
    color: #e0e0e0;
}
.metric-box {
    padding: 10px;
    background-color: #1e1e1e;
    border-radius: 8px;
    color: #f5f5f5;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<div class='centered-title'>1. Auto Shop Performance Dashboard</div>", unsafe_allow_html=True)
st.write(f"**Month Selected:** {month}")

# Online Reputation
st.markdown("<div class='section-header'>2. Online Reputation Summary</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Total Google Reviews", "98", "+4")
col2.metric("Avg Star Rating", "4.1")
col3.metric("Neg. Reviews (30d)", "1")
st.markdown("Top Review Keywords: _Fast_, _Oil Change_, _Friendly_")

# Customer Retention
st.markdown("<div class='section-header'>3. Customer Retention Snapshot</div>", unsafe_allow_html=True)
total_customers = len(filtered_df)
repeat_customers = filtered_df[filtered_df['REPEAT_CUSTOMER'] == 'Yes']
inactive_count = 72  # placeholder
st.write(f"**Total Customers:** {total_customers}")
st.write(f"**Repeat Customers:** {len(repeat_customers)} ({len(repeat_customers)/total_customers*100:.1f}%)")
st.write(f"**Inactive Customers (6+ months):** {inactive_count}")

# Profitability
st.markdown("<div class='section-header'>4. Service Profitability Breakdown</div>", unsafe_allow_html=True)
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
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=10, r=10, t=40, b=10),
    font=dict(color='#e0e0e0', size=13),
    xaxis=dict(title_font=dict(size=14, color='#e0e0e0'), tickfont=dict(size=12, color='#e0e0e0')),
    yaxis=dict(title_font=dict(size=14, color='#e0e0e0'), tickfont=dict(size=12, color='#e0e0e0'))
)
st.plotly_chart(fig, use_container_width=True)

# Additional Insights
st.markdown("<div class='section-header'>7. Deeper Insights</div>", unsafe_allow_html=True)
st.markdown("**1. Technician Efficiency & Utilization**\n- Jobs completed per tech per day\n- Avg labor hours vs. billed hours\n- Idle time between jobs")
st.markdown("**2. Appointment No-Shows & Drop-Off Trends**\n- No-show % by day/time\n- Reschedule rate\n- Lead time before appointments")
st.markdown("**3. Service Package Optimization**\n- Common pairings (e.g., oil + tire rotation)\n- Bundle vs. standalone revenue\n- Package conversion rates")
st.markdown("**4. Parts Inventory vs. Service Demand**\n- Top parts by service type\n- Stock level vs. usage\n- Lost revenue from stockouts")
st.markdown("**5. Lifetime Customer Value (LCV)**\n- Total revenue per customer\n- Visit frequency\n- Changes in spend over time")
st.markdown("**6. Marketing Attribution**\n- Link traffic source to revenue\n- Conversion rate by channel\n- Estimated CAC")

# Summary
st.markdown("<div class='section-header'>6. Summary & Recommendations</div>", unsafe_allow_html=True)
st.markdown("- Strong margins on tire rotation and A/C services.")
st.markdown("- Consider raising prices for brake services.")
st.markdown("- Respond to 2-star review from May 18 to maintain SEO.")
st.markdown("- Send follow-up offer to inactive customers.")

# PDF Export
st.markdown("<div class='section-header'>5. Generate Monthly Report PDF</div>", unsafe_allow_html=True)
if st.button("Generate PDF Summary"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Auto Shop Monthly Summary", ln=1, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Month: {month}", ln=1)
    pdf.cell(200, 10, txt=f"Total Customers: {total_customers}", ln=1)
    pdf.cell(200, 10, txt=f"Repeat Customers: {len(repeat_customers)} ({len(repeat_customers)/total_customers*100:.1f}%)", ln=1)
    pdf.cell(200, 10, txt=f"Inactive Customers: {inactive_count}", ln=1)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Top Services by Profit Margin:", ln=1)
    for _, row in service_profit.head(3).iterrows():
        pdf.cell(200, 10, txt=f"{row['SERVICE_TYPE']}: {row['Profit Margin (%)']}%", ln=1)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Top Services by Profit Margin:", ln=1)
    for _, row in service_profit.head(3).iterrows():
        pdf.cell(200, 10, txt=f"{row['SERVICE_TYPE']}: {row['Profit Margin (%)']}%", ln=1)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Additional Insights", ln=1)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, txt="""
                                1. Technician Efficiency & Utilization
                                - Jobs completed per tech per day
                                - Avg labor hours vs. billed hours
                                - Idle time between jobs
                                
                                2. Appointment No-Shows & Drop-Off Trends
                                - No-show % by day/time
                                - Reschedule rate
                                - Lead time before appointments
                                
                                3. Service Package Optimization
                                - Common pairings (e.g., oil + tire rotation)
                                - Bundle vs. standalone revenue
                                - Package conversion rates
                                
                                4. Parts Inventory vs. Service Demand
                                - Top parts by service type
                                - Stock level vs. usage
                                - Lost revenue from stockouts
                                
                                5. Lifetime Customer Value (LCV)
                                - Total revenue per customer
                                - Visit frequency
                                - Changes in spend over time
                                
                                6. Marketing Attribution
                                - Link traffic source to revenue
                                - Conversion rate by channel
                                - Estimated CAC
                                """)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    b64 = base64.b64encode(pdf_bytes).decode()
    
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="auto_shop_summary.pdf">Download Report PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Auto Shop MVP — Built by Tim Voelker")
