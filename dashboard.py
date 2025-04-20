import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load data
@st.cache_data
def load_data(uploaded_file):
    try:
        data = pd.read_excel(uploaded_file, sheet_name=None)  # Load all sheets as a dictionary
        return data
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Main Streamlit app
st.title("AR Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel workbook (Pivot and Dashboard sheets)", type=["xlsx"])

if uploaded_file:
    # Load data
    sheets = load_data(uploaded_file)

    if sheets:
        # Extract sheets
        pivot_data = sheets.get("Pivot")
        dashboard_data = sheets.get("dashboard 21 april")

        if pivot_data is not None:
            st.subheader("Pivot Data Overview")
            st.dataframe(pivot_data.head())

            # 1. In Scope & Out of Scope
            st.header("In Scope & Out of Scope: Outstanding and Count")
            try:
                scope_data = pivot_data.groupby("Scope Status").agg(
                    Total_Count=("Total Count", "sum"),
                    Total_Outstanding=("Total Outstanding", "sum")
                ).reset_index()
                st.dataframe(scope_data)

                # Pie chart for Outstanding
                scope_pie = px.pie(scope_data, names="Scope Status", values="Total_Outstanding",
                                   title="Outstanding: In Scope vs Out of Scope")
                st.plotly_chart(scope_pie)

            except KeyError as e:
                st.error(f"Missing column for In Scope & Out of Scope analysis: {e}")

            # 2. Collector-Wise Aging
            st.header("Collector-Wise Aging (In Scope)")
            try:
                collector_data = pivot_data[pivot_data["Scope Status"] == "In Scope"]
                aging_data = collector_data.groupby("Collector (AR system)").agg(
                    Bucket_31_60=("31-60", "sum"),
                    Bucket_61_90=("61-90", "sum"),
                    Bucket_91_180=("F_91-180 days", "sum"),
                    Bucket_181_360=("G_181-360 days", "sum"),
                    Bucket_360_plus=("H_360+ days", "sum")
                ).reset_index()
                st.dataframe(aging_data)

                # Stacked bar chart for aging buckets
                aging_chart = px.bar(aging_data, x="Collector (AR system)",
                                     y=["Bucket_31_60", "Bucket_61_90", "Bucket_91_180", "Bucket_181_360", "Bucket_360_plus"],
                                     title="Collector-Wise Aging Buckets (In Scope)",
                                     labels={"value": "Amount", "variable": "Aging Bucket"},
                                     barmode="stack")
                st.plotly_chart(aging_chart)

            except KeyError as e:
                st.error(f"Missing column for Collector-Wise Aging analysis: {e}")

            # 3. Region-Wise Outstanding
            st.header("Region-Wise Outstanding")
            try:
                region_data = pivot_data.groupby("Region").agg(
                    Total_Outstanding=("Outstanding USD (AR system)", "sum")
                ).reset_index()
                st.dataframe(region_data)

                # Pie chart for region-wise outstanding
                region_pie = px.pie(region_data, names="Region", values="Total_Outstanding",
                                    title="Region-Wise Outstanding")
                st.plotly_chart(region_pie)

            except KeyError as e:
                st.error(f"Missing column for Region-Wise Outstanding analysis: {e}")

            # 4. Credit/Debit > 90 Days
            st.header("Credit/Debit > 90 Days")
            try:
                credit_debit_data = pivot_data[pivot_data["Scope Status"] == "In Scope"].groupby("Debit_Credit").agg(
                    Total_Outstanding=("Outstanding USD (AR system)", "sum")
                ).reset_index()
                st.dataframe(credit_debit_data)

                # Bar chart for Credit/Debit > 90 Days
                credit_debit_chart = px.bar(credit_debit_data, x="Debit_Credit", y="Total_Outstanding",
                                            title="Outstanding: Credit/Debit > 90 Days")
                st.plotly_chart(credit_debit_chart)

            except KeyError as e:
                st.error(f"Missing column for Credit/Debit > 90 Days analysis: {e}")

            # 5. Reporting Categories
            st.header("Reporting Categories")
            try:
                reporting_data = pivot_data.groupby("Customer Category Grouping").agg(
                    Total_Outstanding=("Outstanding USD (AR system)", "sum"),
                    Count_Reporting=("Count Reporting", "sum"),
                    Overdue_90_Days=("Overdue > 90 days", "sum"),
                    Target_70_Percent=("70% Target Amount", "sum")
                ).reset_index()
                st.dataframe(reporting_data)

                # Bar chart for reporting categories
                reporting_chart = px.bar(reporting_data, x="Customer Category Grouping", y="Total_Outstanding",
                                         title="Outstanding by Reporting Categories",
                                         labels={"Total_Outstanding": "Outstanding Amount"})
                st.plotly_chart(reporting_chart)

            except KeyError as e:
                st.error(f"Missing column for Reporting Categories analysis: {e}")

        else:
            st.warning("Pivot sheet is missing in the uploaded file.")
    else:
        st.warning("Could not load sheets from the uploaded file.")
else:
    st.info("Please upload your Excel workbook with 'Pivot' and 'dashboard 21 april' sheets.")
