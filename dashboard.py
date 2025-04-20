import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Scope Status Analyzer", layout="wide")

st.title("🔍 Scope Status vs Outstanding USD Analyzer")

# File upload
uploaded_file = st.file_uploader("📁 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    sheet_name = st.text_input("Enter sheet name (leave blank for first sheet):", "")
    
    try:
        # Read Excel
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name or None)
        if isinstance(df, dict):  # Multiple sheets
            df = list(df.values())[0]
        
        # Normalize column names
        df.columns = df.columns.str.strip()
        scope_col = 'Scope Status'
        outstanding_col = 'Outstanding USD (AR system)'

        if scope_col in df.columns and outstanding_col in df.columns:
            st.success("✅ Columns found! Analyzing...")

            # Clean and filter
            filtered_df = df[[scope_col, outstanding_col]].dropna()

            # Grouping
            summary = filtered_df.groupby(scope_col).agg(
                Count=(outstanding_col, 'count'),
                Total_Outstanding=(outstanding_col, 'sum')
            ).reset_index()

            st.subheader("📊 Summary Table")
            st.dataframe(summary.style.format({'Total_Outstanding': '${:,.2f}'}))

            st.subheader("📈 Visualization")
            fig = px.bar(
                summary,
                x=scope_col,
                y='Total_Outstanding',
                color=scope_col,
                text='Count',
                title='Total Outstanding by Scope Status',
                labels={'Total_Outstanding': 'Total Outstanding (USD)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Missing required columns: `{scope_col}` or `{outstanding_col}`")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

else:
    st.info("👈 Upload an Excel file to begin.")
    # ---------------------
# Scope Status Summary
# ---------------------
if scope_col in df.columns and outstanding_col in df.columns:
    st.success("✅ Columns found! Analyzing...")

    # ... (Original Scope Status Summary block here)

    # --------------------------
    # Collector-wise Aging Logic
    # --------------------------
    st.markdown("---")
    st.header("📌 In-Scope Collector Aging Breakdown")

    # (Paste new code block here)

