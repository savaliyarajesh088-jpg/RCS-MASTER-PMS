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

st.caption("RCS MASTER PMS | NSE Portfolio Decision System"
