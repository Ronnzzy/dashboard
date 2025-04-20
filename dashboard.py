import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AR Dashboard", layout="wide")
st.title("📊 AR Aging Dashboard – In Scope & Out of Scope Analysis")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    # Read available sheet names
    xls = pd.ExcelFile(uploaded_file)
    sheet = st.selectbox("Select sheet to analyze", xls.sheet_names)
    df = pd.read_excel(xls, sheet_name=sheet)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Check required columns
    required_cols = [
        'Scope Status', 'Outstanding USD (AR system)', 'Collector Name', 'Region',
        '31-60 day', '61-90 day', '91-180 day', '181-360 day', '360+ day',
        'Overdue > 90 day', 'For Reporting'
    ]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        st.error(f"❌ Missing columns in uploaded file: {', '.join(missing)}")
    else:
        # Convert numeric columns
        numeric_cols = required_cols[1:]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

        # 1. Scope Summary
        scope_summary = df.groupby('Scope Status').agg({
            'Outstanding USD (AR system)': 'sum',
            'Scope Status': 'count'
        }).rename(columns={'Outstanding USD (AR system)': 'Total Outstanding', 'Scope Status': 'Count'})

        st.subheader("1️⃣ In Scope vs Out of Scope Summary")
        st.dataframe(scope_summary)

        # 2. Collector Aging (In Scope)
        in_scope = df[df['Scope Status'].str.strip().str.lower() == 'in scope']
        collector_aging = in_scope.groupby('Collector Name')[
            ['31-60 day', '61-90 day', '91-180 day', '181-360 day', '360+ day', 'Overdue > 90 day']
        ].sum()

        st.subheader("2️⃣ Collector-wise Aging (In Scope Only)")
        st.dataframe(collector_aging)

        # 3. Region-wise Outstanding (In Scope)
        region_outstanding = in_scope.groupby('Region')['Outstanding USD (AR system)'].sum()
        st.subheader("3️⃣ Region-wise Outstanding (In Scope Only)")
        st.dataframe(region_outstanding)

        # 4. Credit vs Debit (Overdue > 90 day)
        credit_debit = in_scope.copy()
        credit_debit['Type'] = credit_debit['Overdue > 90 day'].apply(lambda x: 'Debit' if x > 0 else 'Credit')
        cd_summary = credit_debit.groupby('Type')['Overdue > 90 day'].sum()

        st.subheader("4️⃣ Overdue > 90 Days (Credit vs Debit)")
        st.dataframe(cd_summary)

        # 5. For Reporting Summary (In Scope)
        reporting_summary = in_scope.groupby('For Reporting')['Outstanding USD (AR system)'].sum()
        st.subheader("5️⃣ For Reporting Summary (In Scope Only)")
        st.dataframe(reporting_summary)

        # Optional chart: Collector Aging Stacked Bar
        st.subheader("📊 Collector Aging Chart (Stacked Bar)")
        fig, ax = plt.subplots(figsize=(10, 5))
        collector_aging.plot(kind='bar', stacked=True, ax=ax)
        ax.set_ylabel("Amount")
        ax.set_title("Collector-wise Aging")
        st.pyplot(fig)

else:
    st.info("📎 Please upload an Excel file to get started.")
