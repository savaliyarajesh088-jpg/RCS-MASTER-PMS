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

# =========================
# PORTFOLIO
# =========================

st.header("📁 Portfolio")

try:
    portfolio = pd.read_csv("portfolio.csv")
except Exception as error:
    st.error(f"Portfolio loading error: {error}")
    portfolio = pd.DataFrame()

if portfolio.empty:
    st.warning("Portfolio data not available.")
else:
    st.dataframe(
        portfolio,
        use_container_width=True
    )

st.divider()

# =========================
# NSE + TECHNICAL DATA
# =========================

st.header("📈 NSE & Technical Analysis")

try:

    from src.nse_data import fetch_nse_data

    if portfolio.empty:

        st.warning("No portfolio stocks found.")

    else:

        for symbol in portfolio["SYMBOL"]:

            result = fetch_nse_data(
                str(symbol)
            )

            st.subheader(
                f"📌 {symbol}"
            )

            if result.get("STATUS") != "FRESH":

                st.error(
                    f"Data error: "
                    f"{result.get('STATUS', '--')}"
                )

                continue

            # -------------------------
            # PRICE
            # -------------------------

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "CMP",
                    f"₹{result.get('CMP', '--')}"
                )

            with col2:
                st.metric(
                    "Change %",
                    f"{result.get('CHANGE_%', '--')}%"
                )

            # -------------------------
            # EMA
            # -------------------------

            st.write("### 📊 EMA")

            ema_data = pd.DataFrame(
                {
                    "Indicator": [
                        "EMA 10",
                        "EMA 20",
                        "EMA 50",
                        "EMA 100",
                        "EMA 200"
                    ],
                    "Value": [
                        result.get("EMA_10", "--"),
                        result.get("EMA_20", "--"),
                        result.get("EMA_50", "--"),
                        result.get("EMA_100", "--"),
                        result.get("EMA_200", "--")
                    ]
                }
            )

            st.dataframe(
                ema_data,
                use_container_width=True,
                hide_index=True
            )

            # -------------------------
            # RSI + MACD
            # -------------------------

            st.write("### 📉 Momentum")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "RSI 14",
                    result.get("RSI_14", "--")
                )

            with col2:
                st.metric(
                    "MACD",
                    result.get("MACD", "--")
                )

            with col3:
                st.metric(
                    "MACD Histogram",
                    result.get(
                        "MACD_HIST",
                        "--"
                    )
                )

            # -------------------------
            # TECHNICAL STATUS
            # -------------------------

            st.write("### 🎯 Technical Status")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Technical Score",
                    f"{result.get('TECHNICAL_SCORE', '--')}/100"
                )

            with col2:
                st.metric(
                    "Technical Zone",
                    result.get(
                        "TECHNICAL_ZONE",
                        "--"
                    )
                )

            st.write(
                "EMA Alignment:",
                result.get(
                    "EMA_ALIGNMENT",
                    "--"
                )
            )

            # -------------------------
            # VOLUME + 52W
            # -------------------------

            st.write("### 📦 Volume & 52W")

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"Volume: "
                    f"{result.get('VOLUME', '--')}"
                )

                st.write(
                    f"Volume Ratio: "
                    f"{result.get('VOLUME_RATIO', '--')}x"
                )

            with col2:

                st.write(
                    f"52W High: "
                    f"₹{result.get('52W_HIGH', '--')}"
                )

                st.write(
                    f"52W Low: "
                    f"₹{result.get('52W_LOW', '--')}"
                )

            st.write(
                f"Data Date: "
                f"{result.get('DATA_DATE', '--')}"
            )

            st.write(
                f"Status: "
                f"{result.get('STATUS', '--')}"
            )

            st.divider()

except Exception as error:

    st.error(
        f"Technical engine error: {error}"
    )

# =========================
# PORTFOLIO SUMMARY
# =========================

st.header("📊 Portfolio Summary")

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

# =========================
# CIO ACTION
# =========================

st.header("🎯 CIO Action")

st.info(
    "NSE and Technical Analysis are connected. "
    "Fundamental, Risk and PMS decision engines "
    "will be added next."
)

st.divider()

st.write(
    "RCS MASTER PMS | NSE Portfolio Decision System"
)
