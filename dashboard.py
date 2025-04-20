import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="AR Dashboard")
st.title("📊 Accounts Receivable Dashboard")

# File upload for both Excel files
uploaded_file_master = st.file_uploader("📂 Upload Master Dashboard Excel file", type=["xlsx", "xls"], key="master")
uploaded_file_final = st.file_uploader("📂 Upload Final Dashboard Excel file", type=["xlsx", "xls"], key="final")

if uploaded_file_master and uploaded_file_final:
    try:
        # Load and clean column names for both files
        df_master = pd.read_excel(uploaded_file_master)
        df_final = pd.read_excel(uploaded_file_final)

        # Clean column names
        df_master.columns = df_master.columns.str.strip()
        df_final.columns = df_final.columns.str.strip()

        st.success("✅ Files loaded successfully!")

        # --------------------------------------
        # Visualization 1: Scope Status Summary
        # --------------------------------------
        st.subheader("🔍 In Scope vs Out of Scope Summary")

        # Combine data from both DataFrames if needed
        df_combined = pd.concat([df_master, df_final], ignore_index=True)

        # Ensure the Outstanding column is numeric
        df_combined['Outstanding USD (AR system)'] = pd.to_numeric(df_combined['Outstanding USD (AR system)'], errors='coerce')

        # Group by Scope Status
        scope_summary = df_combined.groupby('Scope Status').agg(
            Count=('Outstanding USD (AR system)', 'count'),
            Total_Outstanding=('Outstanding USD (AR system)', 'sum')
        ).reset_index()

        st.dataframe(scope_summary.style.format({'Total_Outstanding': '${:,.2f}'}))

        # Plotting the Scope Status Summary
        fig_scope = px.bar(
            scope_summary,
            x='Scope Status',
            y='Total_Outstanding',
            color='Scope Status',
            text='Count',
            title='Total Outstanding by Scope Status',
            labels={'Total_Outstanding': 'Outstanding USD'}
        )
        st.plotly_chart(fig_scope, use_container_width=True)

        # --------------------------------------
        # Visualization 2: Collector-wise Aging (In Scope only)
        # --------------------------------------
        st.markdown("---")
        st.header("📌 In-Scope Collector Aging")

        # Filter for In Scope
        in_scope_df = df_combined[df_combined['Scope Status'].str.strip().str.lower() == "in scope"]

        if in_scope_df.empty:
            st.warning("⚠️ No data available for 'In Scope'.")
        else:
            # Group by Collector and sum aging columns
            aging_cols = ['31-60', '61-90', 'F_91-180 days', 'G_181-360 days', 'H_360+ days', 'Overdue > 90 days']
            collector_aging_summary = in_scope_df.groupby('Collector (AR system)')[aging_cols].sum().reset_index()

            # Calculate total outstanding for collectors
            collector_aging_summary['Total_Outstanding'] = in_scope_df.groupby('Collector (AR system)')['Outstanding USD (AR system)'].sum().values

            st.dataframe(collector_aging_summary.style.format('${:,.2f}'))

            # Melt the DataFrame for Plotly
            melted = collector_aging_summary.melt(
                id_vars='Collector (AR system)',
                value_vars=aging_cols,
                var_name="Aging Bucket",
                value_name="Amount"
            )

            # Plotting the Collector-wise Aging
            fig_aging = px.bar(
                melted,
                x="Amount",
                y='Collector (AR system)',
                color="Aging Bucket",
                orientation='h',
                title="Aging by Collector (In Scope Only)",
                height=600
            )
            st.plotly_chart(fig_aging, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error while processing: {str(e)}")
