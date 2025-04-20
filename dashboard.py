import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="AR Dashboard")
st.title("📊 Accounts Receivable Dashboard")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        st.success("✅ File loaded successfully!")
        st.write("### Preview of Uploaded Data")
        st.dataframe(df.head())

        # Show all column names
        st.write("### ✅ Detected Column Names:")
        st.write(df.columns.tolist())

        # Define expected column keys (we’ll match them smartly)
        expected_cols = {
            'Scope Status': 'scope_col',
            'Outstanding USD (AR system)': 'outstanding_col',
            'Collector (AR system)': 'collector_col',
        }

        aging_keywords = ['31-60', '61-90', '91-180', '181-360', '360+', 'Overdue']

        # Match columns smartly
        col_map = {}
        for col in df.columns:
            for expected, key in expected_cols.items():
                if expected.lower() in col.lower():
                    col_map[key] = col
            for aging in aging_keywords:
                if aging.lower() in col.lower():
                    col_map.setdefault('aging', []).append(col)

        missing_keys = [key for key in expected_cols.values() if key not in col_map]
        if missing_keys:
            st.error(f"❌ Missing required columns: {missing_keys}")
        elif 'aging' not in col_map or len(col_map['aging']) < 3:
            st.error(f"❌ Could not detect enough aging columns. Found: {col_map.get('aging', [])}")
        else:
            scope_col = col_map['scope_col']
            outstanding_col = col_map['outstanding_col']
            collector_col = col_map['collector_col']
            aging_cols = col_map['aging']

            # ----------------- SCOPE SUMMARY ----------------
            st.subheader("🔍 In Scope vs Out of Scope")
            scope_summary = df.groupby(scope_col).agg(
                Count=(outstanding_col, 'count'),
                Total_Outstanding=(outstanding_col, 'sum')
            ).reset_index()
            st.dataframe(scope_summary.style.format({'Total_Outstanding': '${:,.2f}'}))

            fig1 = px.bar(
                scope_summary,
                x=scope_col,
                y='Total_Outstanding',
                color=scope_col,
                text='Count',
                title='Total Outstanding by Scope Status',
                labels={'Total_Outstanding': 'Outstanding USD'}
            )
            st.plotly_chart(fig1, use_container_width=True)

            # ----------------- COLLECTOR AGING (IN SCOPE) ----------------
            st.subheader("📌 Collector-wise Aging (Only In Scope)")
            in_scope_df = df[df[scope_col].str.strip().str.lower() == "in scope"]

            collector_aging = in_scope_df.groupby(collector_col)[aging_cols].sum().reset_index()
            st.dataframe(collector_aging.style.format('${:,.2f}'))

            melted = collector_aging.melt(
                id_vars=collector_col,
                var_name="Aging Bucket",
                value_name="Amount"
            )
            fig2 = px.bar(
                melted,
                x="Amount",
                y=collector_col,
                color="Aging Bucket",
                orientation='h',
                title="Aging Breakdown by Collector (In Scope Only)",
                height=600
            )
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
