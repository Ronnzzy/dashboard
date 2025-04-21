import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Accounts Receivable Dashboard", layout="wide")
st.title("📊 Accounts Receivable Dashboard")

uploaded_file = st.file_uploader("📁 Upload Master Dashboard Excel File", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Read relevant sheets
        df_pivot = pd.read_excel(uploaded_file, sheet_name="Pivot")
        df_data = pd.read_excel(uploaded_file, sheet_name="dashboard 21 april")

        st.success("✅ File Uploaded Successfully!")

        # Clean & preprocess
        df_data.columns = df_data.columns.str.strip()
        df_data = df_data[df_data["Scope Status"].notna()]  # Remove blank scope
        df_data["Scope Status"] = df_data["Scope Status"].str.strip()

        # Convert aging columns to numeric (handle blanks)
        aging_cols = ["M. 31-60.", "N. 61-90.", "O. 91-180", "P. 181-360", "Q. 360+ day", "R. Overdue > 90 days"]
        for col in aging_cols:
            df_data[col] = pd.to_numeric(df_data[col], errors='coerce').fillna(0)

        df_data["Outstanding"] = df_data[aging_cols].sum(axis=1)

        # Filter In Scope
        in_scope = df_data[df_data["Scope Status"] == "In Scope"]

        st.header("📌 In Scope vs Out of Scope Summary")
        scope_summary = df_data.groupby("Scope Status").agg(
            Count=("ACCOUNT NO", "nunique"),
            Total_Outstanding=("Outstanding", "sum")
        ).reset_index()
        st.dataframe(scope_summary)

        fig_scope = px.pie(scope_summary, names="Scope Status", values="Total_Outstanding", title="Scope-wise Outstanding")
        st.plotly_chart(fig_scope, use_container_width=True)

        st.header("📌 Collector-wise Aging (Only In Scope)")
        aging_by_collector = in_scope.groupby("COLLECTOR")[aging_cols].sum().reset_index()
        st.dataframe(aging_by_collector)

        fig_collector = px.bar(
            aging_by_collector, x="COLLECTOR", y=aging_cols,
            title="Collector-wise Aging (In Scope Only)",
            barmode="stack"
        )
        st.plotly_chart(fig_collector, use_container_width=True)

        st.header("📌 Region-wise Outstanding (In Scope Only)")
        if "REGION" in in_scope.columns:
            region_summary = in_scope.groupby("REGION")["Outstanding"].sum().reset_index()
            st.dataframe(region_summary)
            fig_region = px.pie(region_summary, names="REGION", values="Outstanding", title="Region-wise Outstanding")
            st.plotly_chart(fig_region, use_container_width=True)

        st.header("📌 90+ Day Credit vs Debit (In Scope Only)")
        in_scope["Overdue_90+"] = in_scope["Q. 181-360 day"] + in_scope["R. 360+ day"]
        credit_debit = in_scope.groupby("CR/DB")["Overdue_90+"].sum().reset_index()
        st.dataframe(credit_debit)
        fig_cd = px.bar(credit_debit, x="CR/DB", y="Overdue_90+", title="Credit/Debit Overdue >90 Days")
        st.plotly_chart(fig_cd, use_container_width=True)

        st.header("📌 For Reporting View (In Scope Only)")
        if "For Reporting" in in_scope.columns:
            reporting_summary = in_scope.groupby("For Reporting")["Outstanding"].sum().reset_index()
            st.dataframe(reporting_summary)
            fig_reporting = px.pie(reporting_summary, names="For Reporting", values="Outstanding", title="For Reporting Distribution")
            st.plotly_chart(fig_reporting, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆ Please upload the Master Dashboard Excel file to begin.")
