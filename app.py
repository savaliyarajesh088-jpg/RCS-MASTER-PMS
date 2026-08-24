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
except Exception as error:
    st.error(f"Portfolio loading error: {error}")
    portfolio = pd.DataFrame()

if not portfolio.empty:
    st.dataframe(
        portfolio,
        use_container_width=True
    )
else:
    st.warning("Portfolio data not available.")

st.divider()

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

            # =========================
            # PRICE
            # =========================

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "CMP",
                    f"₹{result.get('CMP', '--')}"
                )

            with c2:
                st.metric(
                    "Change %",
                    f"{result.get('CHANGE_%', '--')}%"
                )

            # =========================
            # EMA
            # =========================

            st.write("### 📊 EMA")

            e1, e2, e3, e4, e5 = st.columns(5)

            e1.metric(
                "EMA 10",
                f"₹{result.get('EMA_10', '--')}"
            )

            e2.metric(
                "EMA 20",
                f"₹{result.get('EMA_20', '--')}"
            )

            e3.metric(
                "EMA 50",
                f"₹{result.get('EMA_50', '--')}"
            )

            e4.metric(
                "EMA 100",
                f"₹{result.get('EMA_100', '--')}"
            )

            e5.metric(
                "EMA 200",
                f"₹{result.get('EMA_200', '--')}"
            )

            st.write(
                f"EMA Alignment: "
                f"**{result.get('EMA_ALIGNMENT', '--')}**"
            )

            # =========================
            # MOMENTUM
            # =========================

            st.write("### 📉 Momentum")

            m1, m2, m3 = st.columns(3)

            m1.metric(
                "RSI 14",
                result.get(
                    "RSI_14",
                    "--"
                )
            )

            m2.metric(
                "MACD",
                result.get(
                    "MACD",
                    "--"
                )
            )

            m3.metric(
                "MACD Histogram",
                result.get(
                    "MACD_HIST",
                    "--"
                )
            )

            # =========================
            # SUPERTREND
            # =========================

            st.write("### 🔥 Supertrend")

            s1, s2 = st.columns(2)

            s1.metric(
                "Supertrend",
                f"₹{result.get('SUPERTREND', '--')}"
            )

            s2.metric(
                "Trend",
                result.get(
                    "SUPERTREND_STATUS",
                    "--"
                )
            )

            # =========================
            # VOLUME
            # =========================

            st.write("### 📦 Volume & Breakout")

            v1, v2, v3 = st.columns(3)

            v1.metric(
                "Volume",
                result.get(
                    "VOLUME",
                    "--"
                )
            )

            v2.metric(
                "Volume Ratio",
                f"{result.get('VOLUME_RATIO', '--')}x"
            )

            v3.metric(
                "Breakout",
                result.get(
                    "VOLUME_BREAKOUT",
                    "--"
                )
            )

            # =========================
            # PRICE ACTION
            # =========================

            st.write("### 🕯️ Price Action")

            p1, p2 = st.columns(2)

            p1.metric(
                "Price Action",
                result.get(
                    "PRICE_ACTION",
                    "--"
                )
            )

            p2.metric(
                "Body %",
                f"{result.get('BODY_%', '--')}%"
            )

            # =========================
            # 52 WEEK
            # =========================

            h1, h2 = st.columns(2)

            h1.metric(
                "52W High",
                f"₹{result.get('52W_HIGH', '--')}"
            )

            h2.metric(
                "52W Low",
                f"₹{result.get('52W_LOW', '--')}"
            )

            # =========================
            # TECHNICAL SCORE
            # =========================

            st.write("### 🎯 Technical Status")

            t1, t2 = st.columns(2)

            t1.metric(
                "Technical Score",
                f"{result.get('TECHNICAL_SCORE', '--')}/100"
            )

            t2.metric(
                "Technical Zone",
                result.get(
                    "TECHNICAL_ZONE",
                    "--"
                )
            )

            # =========================
            # RISK
            # =========================

            st.write("### 🛡️ Risk Management")

            r1, r2, r3 = st.columns(3)

            r1.metric(
                "ATR 14",
                f"₹{result.get('ATR_14', '--')}"
            )

            r2.metric(
                "Stop Loss",
                f"₹{result.get('STOP_LOSS', '--')}"
            )

            r3.metric(
                "Risk %",
                f"{result.get('RISK_%', '--')}%"
            )

            r4, r5 = st.columns(2)

            r4.metric(
                "Risk Score",
                f"{result.get('RISK_SCORE', '--')}/100"
            )

            r5.metric(
                "Risk Level",
                result.get(
                    "RISK_LEVEL",
                    "--"
                )
            )

            # =========================
            # FINAL SIGNAL
            # =========================

            st.write("### 🚦 Final Signal")

            final_signal = result.get(
                "FINAL_SIGNAL",
                "WAIT"
            )

            if final_signal == "BUY":

                st.success(
                    f"🟢 {final_signal}"
                )

            elif final_signal == "HOLD":

                st.info(
                    f"🟡 {final_signal}"
                )

            elif final_signal == "REDUCE":

                st.warning(
                    f"🟠 {final_signal}"
                )

            else:

                st.error(
                    f"🔴 {final_signal}"
                )

            st.caption(
                f"Data Date: "
                f"{result.get('DATA_DATE', '--')} | "
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

c1, c2, c3 = st.columns(3)

c1.metric(
    "Portfolio Value",
    "₹ —"
)

c2.metric(
    "Portfolio Return",
    "—"
)

c3.metric(
    "Portfolio Health",
    "— / 100"
)

st.divider()

st.header("🎯 CIO Action")

st.info(
    "NSE + Technical + Risk + Signal engines "
    "are connected. Fundamental and PMS decision "
    "engines will be added next."
)

st.divider()

st.write(
    "RCS MASTER PMS | NSE Portfolio Decision System"
)
