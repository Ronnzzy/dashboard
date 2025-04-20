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

        # Define required columns
        scope_col = 'Scope Status'
        outstanding_col = 'Outstanding USD (AR system)'
        collector_col = 'Collector (AR system)'
        aging_cols = [
            '31-60',
            '61-90',
            'F. 91-180 day',
            'G. 181-360 day',
            'H. 360+ day',
            'Overdue > 90 day'
        ]
        all_required_cols = [scope_col, outstanding_col, collector_col] + aging_cols

        missing_cols = [col for col in all_required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing columns in uploaded file: {', '.join(missing_cols)}")
        else:
            # -----------------------------------------
            # ✅ 1. Scope Status Summary (In/Out Scope)
            # -----------------------------------------
            st.markdown("## 🔍 In Scope vs Out of Scope Summary")
            filtered_df = df[[scope_col, outstanding_col]].dropna()
            summary = filtered_df.groupby(scope_col).agg(
                Count=(outstanding_col, 'count'),
                Total_Outstanding=(outstanding_col, 'sum')
            ).reset_index()

            st.dataframe(summary.style.format({'Total_Outstanding': '${:,.2f}'}))

            fig1 = px.bar(
                summary,
                x=scope_col,
                y='Total_Outstanding',
                color=scope_col,
                text='Count',
                title='Total Outstanding by Scope Status',
                labels={'Total_Outstanding': 'Total Outstanding (USD)'}
            )
            st.plotly_chart(fig1, use_container_width=True)

            # -------------------------------------------------
            # ✅ 2. Collector-wise Aging Summary (In Scope Only)
            # -------------------------------------------------
            st.markdown("---")
            st.header("📌 In-Scope Collector Aging Breakdown")

            in_scope_df = df[df[scope_col].str.strip().str.lower() == "in scope"]

            aging_full_cols = [outstanding_col] + aging_cols
            collector_summary = in_scope_df.groupby(collector_col)[aging_full_cols].sum().reset_index()

            st.subheader("📋 Collector-wise Aging Summary (In Scope Only)")
            st.dataframe(collector_summary.style.format('${:,.2f}'))

            st.subheader("📊 Aging Visualization by Collector")
            melt_df = collector_summary.melt(
                id_vars=collector_col,
                var_name="Aging Bucket",
                value_name="Amount"
            )

            fig2 = px.bar(
                melt_df,
                x="Amount",
                y=collector_col,
                color="Aging Bucket",
                orientation='h',
                title="Collector-wise Aging Amount (In Scope Only)",
                labels={"Amount": "USD"},
                height=600
            )
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
