import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load data from uploaded file
def load_data(uploaded_file):
    try:
        # Read the uploaded Excel file
        return pd.read_excel(uploaded_file, sheet_name="Pivot")
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        return None

# Main Streamlit App
st.title("AR Collection Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file (pivot_data.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Load data from the uploaded file
    data = load_data(uploaded_file)
    if data is not None:
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

        # User-defined comparison
        st.header("Data Comparison")
        compare_options = st.multiselect("Select categories or regions to compare", data['Region'].unique())
        if compare_options:
            filtered_data = data[data['Region'].isin(compare_options)]
            compare_fig = px.bar(filtered_data, x='Region', y='Outstanding Amount', color='Region', title='Comparison of Selected Regions')
            st.plotly_chart(compare_fig)
    else:
        st.warning("Unable to process the uploaded file. Please check its content and format.")
else:
    st.info("Please upload the Excel file to generate the dashboard.")
