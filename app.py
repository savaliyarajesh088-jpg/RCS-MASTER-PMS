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
    st.dataframe(portfolio, use_container_width=True)
except Exception:
    st.warning("Portfolio data not available yet.")
    portfolio = pd.DataFrame()

st.divider()

st.header("📈 NSE Market Data")

try:
    from src.nse_data import fetch_nse_data

    if not portfolio.empty:
        for symbol in portfolio["SYMBOL"]:
            result = fetch_nse_data(str(symbol))

            st.subheader(f"📌 {symbol}")

            st.write("CMP:", result.get("CMP", "--"))
            st.write("Change:", result.get("CHANGE", "--"))
            st.write("Change %:", result.get("CHANGE_%", "--"))
            st.write("Volume:", result.get("VOLUME", "--"))
            st.write("Volume Ratio:", result.get("VOLUME_RATIO", "--"))
            st.write("52W High:", result.get("52W_HIGH", "--"))
            st.write("52W Low:", result.get("52W_LOW", "--"))
            st.write("Data Date:", result.get("DATA_DATE", "--"))
            st.write("Status:", result.get("STATUS", "--"))

            st.divider()

    else:
        st.warning("No portfolio stocks found.")

except Exception as error:
    st.error(f"NSE data engine error: {error}")

st.header("📊 Portfolio Summary")

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
    "NSE market data is connected. "
    "Technical and PMS engines will be added next."
)

st.divider()

st.write("RCS MASTER PMS | NSE Portfolio Decision System")
