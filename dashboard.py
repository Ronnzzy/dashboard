import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load the pivot table data (uploaded by the user)
def load_data(uploaded_file):
    try:
        # Load the Excel file into a DataFrame
        return pd.read_excel(uploaded_file, sheet_name="Pivot", skiprows=0)  # Adjust skiprows if necessary
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Streamlit App
st.title("AR Collection Dashboard")

# File uploader for the pivot table
uploaded_file = st.file_uploader("Upload your Excel file (pivot table data)", type=["xlsx"])

if uploaded_file:
    # Load the data
    data = load_data(uploaded_file)

    if data is not None:
        # Display raw data for reference
        st.header("Raw Data (Pivot Table)")
        st.write(data)

        # Overview Section
        st.header("Key Metrics")
        try:
            total_count = data['Total Count'].sum()
            total_outstanding = data['Total Outstanding'].sum()
            overdue_90 = data['Overdue > 90 days'].sum()

            st.metric("Total Count (In Scope)", total_count)
            st.metric("Total Outstanding (In Scope)", f"${total_outstanding:,.2f}")
            st.metric("Total Overdue > 90 Days", f"${overdue_90:,.2f}")
        except KeyError:
            st.error("Columns 'Total Count', 'Total Outstanding', or 'Overdue > 90 days' are missing from the data.")

        # Region-Wise Analysis
        st.header("Outstanding Amount by Region")
        try:
            region_data = data.groupby('Region')['Outstanding USD (AR system)'].sum().reset_index()
            region_fig = px.pie(region_data, names='Region', values='Outstanding USD (AR system)', title='Outstanding by Region')
            st.plotly_chart(region_fig)
        except KeyError:
            st.error("Column 'Region' or 'Outstanding USD (AR system)' is missing from the data.")

        # Aging Buckets Breakdown
        st.header("Aging Buckets Breakdown")
        try:
            aging_buckets = data[['31-60', '61-90', 'F_91-180 days', 'G_181-360 days', 'H_360+ days']].sum()
            aging_df = pd.DataFrame({'Bucket': aging_buckets.index, 'Amount': aging_buckets.values})
            aging_fig = px.bar(aging_df, x='Bucket', y='Amount', color='Bucket', title='Aging Buckets Breakdown')
            st.plotly_chart(aging_fig)
        except KeyError:
            st.error("Aging bucket columns (e.g., '31-60', '61-90') are missing from the data.")

        # Collector Analysis
        st.header("Outstanding Amount by Collector")
        try:
            collector_data = data.groupby('Collector (AR system)')['Outstanding USD (AR system)'].sum().reset_index()
            collector_fig = px.bar(collector_data, x='Collector (AR system)', y='Outstanding USD (AR system)', title='Outstanding by Collector')
            st.plotly_chart(collector_fig)
        except KeyError:
            st.error("Column 'Collector (AR system)' or 'Outstanding USD (AR system)' is missing from the data.")

        # Outstanding Reporting by Category
        st.header("Outstanding Reporting by Category")
        try:
            category_data = data.groupby('Customer Category Grouping')['Outstanding USD (AR system)'].sum().reset_index()
            category_fig = px.bar(category_data, x='Customer Category Grouping', y='Outstanding USD (AR system)', title='Outstanding by Category')
            st.plotly_chart(category_fig)
        except KeyError:
            st.error("Column 'Customer Category Grouping' or 'Outstanding USD (AR system)' is missing from the data.")

        # Comparative Analysis
        st.header("Custom Comparisons")
        filter_options = st.multiselect("Filter by Region or Category",
                                        options=data['Region'].unique() if 'Region' in data.columns else [],
                                        default=None)
        if filter_options:
            comparison_data = data[data['Region'].isin(filter_options)]
            st.write("Filtered Data", comparison_data)
            try:
                comparison_fig = px.bar(comparison_data, x='Region', y='Outstanding USD (AR system)', color='Region', title='Comparison of Selected Regions')
                st.plotly_chart(comparison_fig)
            except KeyError:
                st.error("Column 'Region' or 'Outstanding USD (AR system)' is missing from the filtered data.")
else:
    st.info("Please upload the pivot table file to generate the dashboard.")
