import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="RCS MASTER PMS",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 RCS MASTER PMS")
st.subheader("Portfolio Review & Wealth Creation System")

st.divider()

st.header("📁 Portfolio")

try:
    portfolio = pd.read_csv("portfolio.csv")

    st.dataframe(
        portfolio,
        use_container_width=True
    )

except Exception:
    st.warning("Portfolio data not available yet.")

st.divider()
st.header("📈 NSE Market Data")

try:
    import sys
    import os

    sys.path.append(
        os.path.join(
            os.path.dirname(__file__),
            "src"
        )
    )

    from nse_data import fetch_nse_data

    if not portfolio.empty:
        results = []

        for symbol in portfolio["SYMBOL"]:
            results.append(
                fetch_nse_data(str(symbol))
            )

        market_df = pd.DataFrame(results)

        st.dataframe(
            market_df,
            use_container_width=True
        )
    else:
        st.warning("No portfolio stocks found.")

except Exception as error:
    st.error(
        f"NSE data engine error: {error}"
    )

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Portfolio Value", "₹ --")

with col2:
    st.metric("Portfolio Return", "--")

with col3:
    st.metric("Portfolio Health", "-- / 100")

st.divider()

st.header("🎯 CIO Action")

st.info(
    "Portfolio analysis will appear here "
    "after the NSE and PMS engines are connected."
)

st.divider()

st.write("RCS MASTER PMS | NSE Portfolio Decision System")
