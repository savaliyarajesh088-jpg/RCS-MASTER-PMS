import streamlit as st

st.set_page_config(
    page_title="RCS MASTER PMS",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 RCS MASTER PMS")
st.subheader("Portfolio Review & Wealth Creation System")

st.info(
    "NSE Portfolio Analysis Dashboard"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Portfolio Value",
        "₹ --"
    )

with col2:
    st.metric(
        "Portfolio Return",
        "--"
    )

with col3:
    st.metric(
        "Portfolio Health",
        "-- / 100"
    )

st.divider()

st.header("📊 PMS Dashboard")

st.write(
    "Portfolio data will appear here "
    "after the data engine is connected."
)

st.header("🎯 CIO Action")

st.warning(
    "No portfolio data loaded yet."
)

st.divider()

st.caption(
    "RCS MASTER PMS | "
    "Portfolio Decision-Support System"
)
