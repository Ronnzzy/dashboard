import streamlit as st
import pandas as pd
import plotly.express as px

# Load your pivot table data
@st.cache
def load_data():
    # Replace with your actual data loading logic
    return pd.read_excel("pivot_data.xlsx", sheet_name="Pivot")

data = load_data()

# Title
st.title("AR Collection Dashboard")

# Overview Section
st.header("Overview")
total_count = data['Total Count'].sum()
total_outstanding = data['Total Outstanding'].sum()
total_overdue_90 = data['Overdue > 90 Days'].sum()

st.metric("Total Count (In Scope)", total_count)
st.metric("Total Outstanding (In Scope)", f"${total_outstanding:,.2f}")
st.metric("Total Overdue > 90 Days", f"${total_overdue_90:,.2f}")

# Region-Wise Pie Chart
st.header("Outstanding Region-Wise")
region_fig = px.pie(data, names='Region', values='Outstanding Amount', title='Outstanding by Region')
st.plotly_chart(region_fig)

# Aging Buckets Breakdown
st.header("Aging Buckets Breakdown")
aging_fig = px.bar(data, x='Bucket', y='Amount', color='Bucket', title='Aging Buckets Breakdown')
st.plotly_chart(aging_fig)

st.write("One-click dashboard powered by Streamlit.")
