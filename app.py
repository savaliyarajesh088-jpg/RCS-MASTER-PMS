import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from src.nse_data import fetch_nse_data
from src.fundamental_engine import fetch_fundamental_data


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="R.S MASTER STOCK GUIDE",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 0.7rem;
    padding-bottom: 1rem;
    padding-left: 0.6rem;
    padding-right: 0.6rem;
    max-width: 1200px;
}

.main-title {
    text-align:center;
    font-size:1.65rem;
    font-weight:900;
    margin-bottom:0;
}

.sub-title {
    text-align:center;
    font-size:0.85rem;
    opacity:0.75;
    margin-bottom:0.7rem;
}

.stock-card {
    border:1px solid rgba(128,128,128,.25);
    border-radius:16px;
    padding:14px;
    margin-top:10px;
    margin-bottom:16px;
    background:rgba(128,128,128,.035);
}

.big-price {
    font-size:1.55rem;
    font-weight:900;
}

.guide-card {
    border-radius:14px;
    padding:13px;
    text-align:center;
    font-weight:800;
    margin:8px 0;
    border:1px solid rgba(128,128,128,.25);
}

.green {
    background:rgba(0,180,80,.12);
}

.yellow {
    background:rgba(240,180,0,.12);
}

.orange {
    background:rgba(255,130,0,.12);
}

.red {
    background:rgba(220,40,40,.12);
}

.blue {
    background:rgba(40,120,220,.12);
}

.zone-card {
    border-radius:12px;
    padding:10px;
    text-align:center;
    font-weight:800;
    margin:8px 0;
}

.target-card {
    border:1px solid rgba(128,128,128,.25);
    border-radius:12px;
    padding:10px;
    text-align:center;
}

.small-text {
    font-size:.72rem;
    opacity:.7;
}

@media(max-width:640px) {

    .main-title {
        font-size:1.3rem;
    }

    .sub-title {
        font-size:.7rem;
    }

    .block-container {
        padding-left:.4rem;
        padding-right:.4rem;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">📈 R.S MASTER STOCK GUIDE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'NSE • Technical • Fundamental • Momentum • Risk • Target'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# PORTFOLIO LOAD
# =========================================================

try:
    portfolio = pd.read_csv("portfolio.csv")
except Exception as error:
    st.error(f"Portfolio loading error: {error}")
    portfolio = pd.DataFrame()


if portfolio.empty:
    st.warning("પોર્ટફોલિયો ડેટા ઉપલબ્ધ નથી.")
    st.stop()


# =========================================================
# PORTFOLIO
# =========================================================

st.subheader("📁 પોર્ટફોલિયો")

st.dataframe(
    portfolio,
    use_container_width=True,
    hide_index=True
)

st.divider()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_float(value, default=0):
    try:
        if value is None:
            return default
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def get_zone(score):
    if score >= 75:
        return "🐂 BULL"
    elif score >= 50:
        return "🐷 PIG"
    else:
        return "🐻 BEAR"


def get_zone_class(zone):
    if "BULL" in zone:
        return "green"
    elif "PIG" in zone:
        return "yellow"
    return "red"


def get_master_decision(score):
    if score >= 80:
        return "🔥 STRONG BUY", "green"
    elif score >= 70:
        return "🟢 BUY", "green"
    elif score >= 60:
        return "🟡 BUY ON DIP", "yellow"
    elif score >= 45:
        return "⏳ WAIT", "yellow"
    elif score >= 30:
        return "🟠 REDUCE", "orange"
    return "🔴 EXIT", "red"


def calculate_targets(cmp, atr, technical_score, fundamental_score):

    cmp = safe_float(cmp)
    atr = safe_float(atr)

    if cmp <= 0:
        return None, None, None

    # ---------------------------------------------
    # Swing Target
    # ---------------------------------------------

    swing_multiplier = 3.0

    if technical_score >= 80:
        swing_multiplier = 4.0
    elif technical_score >= 65:
        swing_multiplier = 3.5
    elif technical_score >= 50:
        swing_multiplier = 3.0
    else:
        swing_multiplier = 2.0

    swing_target = cmp + (atr * swing_multiplier)

    # ---------------------------------------------
    # Long-Term Target
    # ---------------------------------------------

    long_multiplier = 8.0

    if fundamental_score >= 80:
        long_multiplier = 12.0
    elif fundamental_score >= 65:
        long_multiplier = 10.0
    elif fundamental_score >= 50:
        long_multiplier = 8.0
    else:
        long_multiplier = 5.0

    long_target = cmp + (atr * long_multiplier)

    # ---------------------------------------------
    # Common Stop Loss
    # ---------------------------------------------

    common_sl = cmp - (atr * 2)

    return (
        round(swing_target, 2),
        round(long_target, 2),
        round(max(common_sl, 0), 2)
    )


def get_momentum_level(result):

    cmp = safe_float(result.get("CMP"))
    ema10 = safe_float(result.get("EMA_10"))
    ema20 = safe_float(result.get("EMA_20"))
    ema50 = safe_float(result.get("EMA_50"))

    levels = [
        value for value in
        [ema10, ema20, ema50]
        if value > 0
    ]

    if not levels:
        return None

    resistance = max(levels)

    if cmp > resistance:
        return cmp

    return resistance


# =========================================================
# CHART
# =========================================================

def show_chart(symbol):

    try:

        ticker = (
            symbol
            if symbol.endswith(".NS")
            else symbol + ".NS"
        )

        chart_data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if chart_data.empty:
            st.warning("ચાર્ટ ડેટા ઉપલબ્ધ નથી.")
            return

        if isinstance(
            chart_data.columns,
            pd.MultiIndex
        ):
            chart_data.columns = (
                chart_data.columns
                .get_level_values(0)
            )

        chart_data = chart_data.dropna()

        if chart_data.empty:
            return

        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=chart_data.index,
                open=chart_data["Open"],
                high=chart_data["High"],
                low=chart_data["Low"],
                close=chart_data["Close"],
                name="Price"
            )
        )

        close = chart_data["Close"]

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=close.ewm(
                    span=20,
                    adjust=False
                ).mean(),
                name="EMA 20",
                line=dict(width=1)
            )
        )

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=close.ewm(
                    span=50,
                    adjust=False
                ).mean(),
                name="EMA 50",
                line=dict(width=1)
            )
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=5,
                r=5,
                t=25,
                b=5
            ),
            xaxis_rangeslider_visible=False,
            legend=dict(
                orientation="h"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as error:

        st.warning(
            f"ચાર્ટ error: {error}"
        )


# =========================================================
# STOCK LOOP
# =========================================================

for symbol in portfolio["SYMBOL"]:

    symbol = str(
        symbol
    ).strip().upper()

    # =====================================================
    # NSE
    # =====================================================

    result = fetch_nse_data(symbol)

    if result.get("STATUS") != "FRESH":

        st.error(
            f"{symbol}: NSE data unavailable — "
            f"{result.get('STATUS', '--')}"
        )

        continue


    # =====================================================
    # FUNDAMENTAL
    # =====================================================

    fundamental = fetch_fundamental_data(
        symbol
    )


    # =====================================================
    # SCORES
    # =====================================================

    technical_score = safe_float(
        result.get(
            "TECHNICAL_SCORE"
        )
    )

    fundamental_score = safe_float(
        fundamental.get(
            "FUNDAMENTAL_SCORE"
        )
    )

    risk_score = safe_float(
        result.get(
            "RISK_SCORE"
        )
    )


    # =====================================================
    # MASTER SCORE
    # =====================================================

    master_score = (
        technical_score * 0.40
        +
        fundamental_score * 0.40
        +
        risk_score * 0.20
    )

    master_score = round(
        master_score,
        1
    )


    # =====================================================
    # DECISION
    # =====================================================

    decision, decision_class = (
        get_master_decision(
            master_score
        )
    )


    # =====================================================
    # ZONE
    # =====================================================

    zone = get_zone(
        master_score
    )

    zone_class = get_zone_class(
        zone
    )


    # =====================================================
    # TARGET + SL
    # =====================================================

    cmp = safe_float(
        result.get("CMP")
    )

    atr = safe_float(
        result.get("ATR_14")
    )

    swing_target, long_target, common_sl = (
        calculate_targets(
            cmp,
            atr,
            technical_score,
            fundamental_score
        )
    )


    # =====================================================
    # MOMENTUM
    # =====================================================

    momentum_price = get_momentum_level(
        result
    )


    # =====================================================
    # STOCK CARD
    # =====================================================

    st.markdown(
        '<div class="stock-card">',
        unsafe_allow_html=True
    )

    st.subheader(
        f"📌 {symbol}"
    )


    # =====================================================
    # PRICE
    # =====================================================

    p1, p2, p3 = st.columns(3)

    p1.metric(
        "CMP",
        f"₹{cmp:.2f}"
    )

    p2.metric(
        "બદલાવ",
        f"{safe_float(result.get('CHANGE_%')):.2f}%"
    )

    p3.metric(
        "Momentum Level",
        (
            f"₹{momentum_price:.2f}"
            if momentum_price
            else "--"
        )
    )


    # =====================================================
    # MASTER
    # =====================================================

    st.markdown(
        f"""
        <div class="guide-card {decision_class}">
            🏦 MASTER SCORE<br>
            <span style="font-size:1.5rem">
                {master_score}/100
            </span>
            <br>
            {decision}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # ZONE
    # =====================================================

    st.markdown(
        f"""
        <div class="zone-card {zone_class}">
            MARKET ZONE<br>
            {zone}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # TARGET / SL
    # =====================================================

    st.markdown(
        "### 🎯 Target & Risk"
    )

    t1, t2, t3 = st.columns(3)

    t1.metric(
        "Swing Target",
        (
            f"₹{swing_target:.2f}"
            if swing_target
            else "--"
        )
    )

    t2.metric(
        "Long-Term Target",
        (
            f"₹{long_target:.2f}"
            if long_target
            else "--"
        )
    )

    t3.metric(
        "Common Stop Loss",
        (
            f"₹{common_sl:.2f}"
            if common_sl
            else "--"
        )
    )


    # =====================================================
    # BUY / DIP LOGIC
    # =====================================================

    if decision == "🔥 STRONG BUY":

        st.success(
            "🔥 Strong Buy — Momentum + Quality strong"
        )

    elif decision == "🟢 BUY":

        st.success(
            "🟢 Buy — Setup positive"
        )

    elif decision == "🟡 BUY ON DIP":

        st.warning(
            "🟡 Buy on Dip — હાલના ભાવ પાછળ ન દોડવું"
        )

    elif decision == "⏳ WAIT":

        st.info(
            "⏳ Wait — confirmation જરૂરી"
        )

    elif decision == "🟠 REDUCE":

        st.warning(
            "🟠 Reduce — risk/reward weak"
        )

    else:

        st.error(
            "🔴 Exit — setup weak"
        )


    # =====================================================
    # CHART
    # =====================================================

    st.markdown(
        "### 📊 Price Chart"
    )

    show_chart(
        symbol
    )


    # =====================================================
    # TECHNICAL
    # =====================================================

    st.markdown(
        "### 📈 ટેક્નિકલ"
    )

    a1, a2, a3 = st.columns(3)

    a1.metric(
        "Technical Score",
        f"{technical_score:.0f}/100"
    )

    a2.metric(
        "Technical Zone",
        result.get(
            "TECHNICAL_ZONE",
            "--"
        )
    )

    a3.metric(
        "RSI 14",
        result.get(
            "RSI_14",
            "--"
        )
    )


    # =====================================================
    # EMA
    # =====================================================

    st.caption(
        "📊 EMA"
    )

    e1, e2, e3, e4, e5 = st.columns(5)

    e1.metric(
        "10",
        f"₹{safe_float(result.get('EMA_10')):.2f}"
    )

    e2.metric(
        "20",
        f"₹{safe_float(result.get('EMA_20')):.2f}"
    )

    e3.metric(
        "50",
        f"₹{safe_float(result.get('EMA_50')):.2f}"
    )

    e4.metric(
        "100",
        f"₹{safe_float(result.get('EMA_100')):.2f}"
    )

    e5.metric(
        "200",
        f"₹{safe_float(result.get('EMA_200')):.2f}"
    )

    st.caption(
        "EMA Alignment: "
        f"**{result.get('EMA_ALIGNMENT', '--')}**"
    )


    # =====================================================
    # MOMENTUM
    # =====================================================

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "RSI",
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
        "Histogram",
        result.get(
            "MACD_HIST",
            "--"
        )
    )


    # =====================================================
    # SUPERTREND
    # =====================================================

    s1, s2 = st.columns(2)

    s1.metric(
        "Supertrend",
        f"₹{safe_float(result.get('SUPERTREND')):.2f}"
    )

    s2.metric(
        "Trend",
        result.get(
            "SUPERTREND_STATUS",
            "--"
        )
    )


    # =====================================================
    # VOLUME
    # =====================================================

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
        f"{safe_float(result.get('VOLUME_RATIO')):.2f}x"
    )

    v3.metric(
        "Breakout",
        result.get(
            "VOLUME_BREAKOUT",
            "--"
        )
    )


    # =====================================================
    # FUNDAMENTAL
    # =====================================================

    st.markdown(
        "### 🏢 ફન્ડામેન્ટલ"
    )

    f1, f2, f3 = st.columns(3)

    f1.metric(
        "Fundamental Score",
        f"{fundamental_score:.0f}/100"
    )

    f2.metric(
        "Zone",
        fundamental.get(
            "FUNDAMENTAL_ZONE",
            "--"
        )
    )

    f3.metric(
        "Data Quality",
        f"{safe_float(fundamental.get('DATA_QUALITY_%')):.0f}%"
    )


    f4, f5, f6 = st.columns(3)

    f4.metric(
        "Revenue Growth",
        f"{safe_float(fundamental.get('REVENUE_GROWTH_%')):.2f}%"
    )

    f5.metric(
        "Profit Growth",
        f"{safe_float(fundamental.get('PROFIT_GROWTH_%')):.2f}%"
    )

    f6.metric(
        "ROE",
        (
            f"{fundamental.get('ROE_%')}%"
            if fundamental.get("ROE_%") is not None
            else "--"
        )
    )


    # =====================================================
    # RISK
    # =====================================================

    st.markdown(
        "### 🛡️ જોખમ"
    )

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Risk Score",
        f"{risk_score:.0f}/100"
    )

    r2.metric(
        "Risk Level",
        result.get(
            "RISK_LEVEL",
            "--"
        )
    )

    r3.metric(
        "Risk %",
        f"{safe_float(result.get('RISK_%')):.2f}%"
    )


    # =====================================================
    # DATA
    # =====================================================

    st.caption(
        f"📅 Data Date: "
        f"{result.get('DATA_DATE', '--')}  |  "
        f"Status: "
        f"{result.get('STATUS', '--')}"
    )


    # =====================================================
    # COPY / SHARE
    # =====================================================

    guide_text = f"""
R.S MASTER STOCK GUIDE

Stock: {symbol}
CMP: ₹{cmp:.2f}

MASTER SCORE: {master_score}/100
DECISION: {decision}
ZONE: {zone}

Technical Score: {technical_score:.0f}/100
Fundamental Score: {fundamental_score:.0f}/100
Risk Score: {risk_score:.0f}/100

Swing Target: ₹{swing_target if swing_target else '--'}
Long-Term Target: ₹{long_target if long_target else '--'}
Common Stop Loss: ₹{common_sl if common_sl else '--'}

Momentum Level: ₹{momentum_price if momentum_price else '--'}

Technical Zone: {result.get('TECHNICAL_ZONE', '--')}
RSI: {result.get('RSI_14', '--')}
MACD: {result.get('MACD', '--')}
Supertrend: {result.get('SUPERTREND_STATUS', '--')}
Volume Breakout: {result.get('VOLUME_BREAKOUT', '--')}

Data Date: {result.get('DATA_DATE', '--')}
"""

    st.code(
        guide_text,
        language="text"
    )

    st.download_button(
        "📤 Share / Download Stock Report",
        data=guide_text,
        file_name=f"{symbol}_stock_guide.txt",
        mime="text/plain",
        key=f"share_{symbol}"
    )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()


# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

st.header("📊 પોર્ટફોલિયો સારાંશ")

st.info(
    "R.S MASTER STOCK GUIDE: "
    "NSE + Technical + Fundamental + Momentum + Risk + "
    "Swing Target + Long-Term Target + Common Stop Loss."
)


# =========================================================
# FOOTER
# =========================================================

st.caption(
    "📈 R.S MASTER STOCK GUIDE | NSE Stock Decision System"
)
