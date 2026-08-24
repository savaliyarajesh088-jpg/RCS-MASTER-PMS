import streamlit as st
import pandas as pd

from src.nse_data import fetch_nse_data
from src.fundamental_engine import fetch_fundamental_data


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


if portfolio.empty:
    st.warning("Portfolio data not available.")
    st.stop()


st.dataframe(
    portfolio,
    use_container_width=True
)

st.divider()


st.header("📈 NSE & Technical Analysis")


for symbol in portfolio["SYMBOL"]:

    symbol = str(symbol).strip().upper()

    result = fetch_nse_data(symbol)

    st.subheader(f"📌 {symbol}")

    if result.get("STATUS") != "FRESH":
        st.error(
            f"NSE Data Error: "
            f"{result.get('STATUS', '--')}"
        )
        continue


    c1, c2 = st.columns(2)

    c1.metric(
        "CMP",
        f"₹{result.get('CMP', '--')}"
    )

    c2.metric(
        "Change %",
        f"{result.get('CHANGE_%', '--')}%"
    )


    st.write("### 📊 EMA")

    e1, e2, e3, e4, e5 = st.columns(5)

    e1.metric("EMA 10", f"₹{result.get('EMA_10', '--')}")
    e2.metric("EMA 20", f"₹{result.get('EMA_20', '--')}")
    e3.metric("EMA 50", f"₹{result.get('EMA_50', '--')}")
    e4.metric("EMA 100", f"₹{result.get('EMA_100', '--')}")
    e5.metric("EMA 200", f"₹{result.get('EMA_200', '--')}")

    st.write(
        f"EMA Alignment: **{result.get('EMA_ALIGNMENT', '--')}**"
    )


    st.write("### 📉 Momentum")

    m1, m2, m3 = st.columns(3)

    m1.metric("RSI 14", result.get("RSI_14", "--"))
    m2.metric("MACD", result.get("MACD", "--"))
    m3.metric("MACD Histogram", result.get("MACD_HIST", "--"))


    st.write("### 🔥 Supertrend")

    s1, s2 = st.columns(2)

    s1.metric(
        "Supertrend",
        f"₹{result.get('SUPERTREND', '--')}"
    )

    s2.metric(
        "Trend",
        result.get("SUPERTREND_STATUS", "--")
    )


    st.write("### 📦 Volume & Breakout")

    v1, v2, v3 = st.columns(3)

    v1.metric("Volume", result.get("VOLUME", "--"))
    v2.metric(
        "Volume Ratio",
        f"{result.get('VOLUME_RATIO', '--')}x"
    )
    v3.metric(
        "Breakout",
        result.get("VOLUME_BREAKOUT", "--")
    )


    st.write("### 🕯️ Price Action")

    p1, p2 = st.columns(2)

    p1.metric(
        "Price Action",
        result.get("PRICE_ACTION", "--")
    )

    p2.metric(
        "Body %",
        f"{result.get('BODY_%', '--')}%"
    )


    h1, h2 = st.columns(2)

    h1.metric(
        "52W High",
        f"₹{result.get('52W_HIGH', '--')}"
    )

    h2.metric(
        "52W Low",
        f"₹{result.get('52W_LOW', '--')}"
    )


    st.write("### 🎯 Technical Status")

    t1, t2 = st.columns(2)

    t1.metric(
        "Technical Score",
        f"{result.get('TECHNICAL_SCORE', '--')}/100"
    )

    t2.metric(
        "Technical Zone",
        result.get("TECHNICAL_ZONE", "--")
    )


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
        result.get("RISK_LEVEL", "--")
    )


    st.write("### 🚦 Technical Final Signal")

    final_signal = result.get(
        "FINAL_SIGNAL",
        "WAIT"
    )

    if final_signal == "BUY":
        st.success("🟢 BUY")
    elif final_signal == "HOLD":
        st.info("🟡 HOLD")
    elif final_signal == "REDUCE":
        st.warning("🟠 REDUCE")
    elif final_signal == "EXIT":
        st.error("🔴 EXIT")
    else:
        st.warning("🟡 WAIT")


    st.caption(
        f"Data Date: {result.get('DATA_DATE', '--')} | "
        f"Status: {result.get('STATUS', '--')}"
    )


    # =====================================================
    # FUNDAMENTAL
    # =====================================================

    st.write("### 🏢 Fundamental Analysis")

    fundamental = fetch_fundamental_data(symbol)


    if fundamental.get("FUNDAMENTAL_STATUS") == "FRESH":

        st.write("### 📈 Growth")

        f1, f2, f3 = st.columns(3)

        f1.metric(
            "Revenue Growth",
            f"{fundamental.get('REVENUE_GROWTH_%', '--')}%"
        )

        f2.metric(
            "Profit Growth",
            f"{fundamental.get('PROFIT_GROWTH_%', '--')}%"
        )

        f3.metric(
            "ROE",
            f"{fundamental.get('ROE_%', '--')}%"
        )


        st.write("### 🏆 Quality")

        f4, f5, f6 = st.columns(3)

        f4.metric(
            "ROA",
            f"{fundamental.get('ROA_%', '--')}%"
        )

        f5.metric(
            "Debt / Equity",
            fundamental.get(
                "DEBT_TO_EQUITY",
                "--"
            )
        )

        f6.metric(
            "Profit Margin",
            f"{fundamental.get('PROFIT_MARGIN_%', '--')}%"
        )


        st.write("### 💰 Valuation")

        q1, q2 = st.columns(2)

        q1.metric(
            "PE",
            fundamental.get("PE", "--")
        )

        q2.metric(
            "Forward PE",
            fundamental.get("FORWARD_PE", "--")
        )


        st.write("### 🎯 Fundamental Score")

        fs1, fs2, fs3 = st.columns(3)

        fs1.metric(
            "Fundamental Score",
            f"{fundamental.get('FUNDAMENTAL_SCORE', '--')}/100"
        )

        fs2.metric(
            "Fundamental Zone",
            fundamental.get(
                "FUNDAMENTAL_ZONE",
                "--"
            )
        )

        fs3.metric(
            "Data Quality",
            f"{fundamental.get('DATA_QUALITY_%', '--')}%"
        )


        st.write("### 📊 Fundamental Score Breakdown")

        b1, b2, b3 = st.columns(3)

        b1.metric(
            "Growth Score",
            f"{fundamental.get('GROWTH_SCORE', '--')}/40"
        )

        b2.metric(
            "Quality Score",
            f"{fundamental.get('QUALITY_SCORE', '--')}/40"
        )

        b3.metric(
            "Valuation Score",
            f"{fundamental.get('VALUATION_SCORE', '--')}/20"
        )


        st.caption(
            f"Fundamental Data Quality: "
            f"{fundamental.get('DATA_QUALITY', '--')}"
        )

    else:

        st.warning(
            "Fundamental data not available."
        )

        if fundamental.get("ERROR"):
            st.caption(
                fundamental.get("ERROR")
            )


    # =====================================================
    # PMS MASTER SCORE
    # =====================================================

    st.write("### 🏦 PMS Master Score")

    try:
        technical_score = float(
            result.get("TECHNICAL_SCORE", 0) or 0
        )
    except Exception:
        technical_score = 0


    try:
        fundamental_score = float(
            fundamental.get("FUNDAMENTAL_SCORE", 0) or 0
        )
    except Exception:
        fundamental_score = 0


    try:
        risk_score = float(
            result.get("RISK_SCORE", 0) or 0
        )
    except Exception:
        risk_score = 0


    pms_score = round(
        technical_score * 0.40
        + fundamental_score * 0.40
        + risk_score * 0.20,
        1
    )


    if pms_score >= 80:
        cio_decision = "ADD"
    elif pms_score >= 65:
        cio_decision = "HOLD"
    elif pms_score >= 50:
        cio_decision = "WAIT"
    elif pms_score >= 35:
        cio_decision = "REDUCE"
    else:
        cio_decision = "EXIT"


    ps1, ps2, ps3 = st.columns(3)

    ps1.metric(
        "PMS Master Score",
        f"{pms_score}/100"
    )

    ps2.metric(
        "Technical",
        f"{technical_score:.1f}/100"
    )

    ps3.metric(
        "Fundamental",
        f"{fundamental_score:.1f}/100"
    )


    ps4, ps5 = st.columns(2)

    ps4.metric(
        "Risk",
        f"{risk_score:.1f}/100"
    )

    ps5.metric(
        "CIO Decision",
        cio_decision
    )


    if cio_decision == "ADD":
        st.success("🟢 CIO ACTION — ADD")

    elif cio_decision == "HOLD":
        st.info("🟢 CIO ACTION — HOLD")

    elif cio_decision == "WAIT":
        st.warning("🟡 CIO ACTION — WAIT")

    elif cio_decision == "REDUCE":
        st.warning("🟠 CIO ACTION — REDUCE")

    else:
        st.error("🔴 CIO ACTION — EXIT")


    st.divider()


# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

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


# =========================================================
# CIO ACTION
# =========================================================

st.divider()

st.header("🎯 CIO Action")

st.info(
    "NSE + Technical + Risk + Fundamental "
    "engines are connected. PMS Master Score "
    "and CIO Decision Engine are active."
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.write(
    "RCS MASTER PMS | NSE Portfolio Decision System"
)
