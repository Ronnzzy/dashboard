import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="AR Dashboard")
st.title("📊 Accounts Receivable Dashboard")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Load and clean column names
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        st.success("✅ File loaded successfully!")
        st.write("### Sample Data")
        st.dataframe(df.head())

        # Define columns
        scope_col = 'Scope Status'  # H
        outstanding_col = 'Outstanding USD (AR system)'  # K
        collector_col = 'Collector (AR system)'  # G
        aging_cols = [  # M to R
            '31-60',
            '61-90',
            'F. 91-180 day',
            'G. 181-360 day',
            'H. 360+ day',
            'Overdue > 90 day'
        ]
        required_cols = [scope_col, outstanding_col, collector_col] + aging_cols
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing columns in uploaded file: {', '.join(missing_cols)}")
        else:
            # --------------------------------------
            # ✅ 1. Scope Status Summary
            # --------------------------------------
            st.subheader("🔍 In Scope vs Out of Scope Summary")

            # Ensure the outstanding column is numeric
            df[outstanding_col] = pd.to_numeric(df[outstanding_col], errors='coerce')

            scope_summary = df.groupby(scope_col).agg(
                Count=(outstanding_col, 'count'),
                Total_Outstanding=(outstanding_col, 'sum')
            ).reset_index()

            st.dataframe(scope_summary.style.format({'Total_Outstanding': '${:,.2f}'}))

            fig_scope = px.bar(
                scope_summary,
                x=scope_col,
                y='Total_Outstanding',
                color=scope_col,
                text='Count',
                title='Total Outstanding by Scope Status',
                labels={'Total_Outstanding': 'Outstanding USD'}
            )
            st.plotly_chart(fig_scope, use_container_width=True)

            # --------------------------------------
            # ✅ 2. Collector-wise Aging (In Scope only)
            # --------------------------------------
            st.markdown("---")
            st.header("📌 In-Scope Collector Aging (Based on Columns M–R)")

            in_scope_df = df[df[scope_col].str.strip().str.lower() == "in scope"]

            if in_scope_df.empty:
                st.warning("⚠️ No data available for 'In Scope'.")
            else:
                collector_aging_summary = in_scope_df.groupby(collector_col)[aging_cols].sum().reset_index()

                st.dataframe(collector_aging_summary.style
