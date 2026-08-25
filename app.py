import streamlit as st
import pandas as pd
import numpy as np
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
# MOBILE UI
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        padding-left: 0.45rem;
        padding-right: 0.45rem;
        max-width: 1200px;
    }

    .main-title {
        text-align: center;
        font-size: 1.55rem;
        font-weight: 900;
        margin-bottom: 0;
    }

    .sub-title {
        text-align: center;
        font-size: 0.72rem;
        opacity: 0.75;
        margin-bottom: 0.6rem;
    }

    .stock-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        padding: 12px;
        margin-top: 8px;
        margin-bottom: 15px;
        background: rgba(128,128,128,0.035);
    }

    .score-card {
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        border: 1px solid rgba(128,128,128,0.25);
    }

    .score-title {
        font-size: 0.7rem;
        opacity: 0.7;
        font-weight: 800;
    }

    .score-value {
        font-size: 1.45rem;
        font-weight: 900;
    }

    .decision-card {
        border-radius: 14px;
        padding: 11px;
        text-align: center;
        font-size: 1rem;
        font-weight: 900;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    .green {
        background: rgba(0,180,80,0.12);
        border: 1px solid rgba(0,180,80,0.35);
    }

    .yellow {
        background: rgba(240,180,0,0.12);
        border: 1px solid rgba(240,180,0,0.35);
    }

    .orange {
        background: rgba(255,130,0,0.12);
        border: 1px solid rgba(255,130,0,0.35);
    }

    .red {
        background: rgba(220,40,40,0.12);
        border: 1px solid rgba(220,40,40,0.35);
    }

    .blue {
        background: rgba(40,120,220,0.12);
        border: 1px solid rgba(40,120,220,0.35);
    }

    .section-title {
        font-size: 1rem;
        font-weight: 900;
        margin-top: 12px;
        margin-bottom: 7px;
    }

    @media (max-width: 640px) {

        .block-container {
            padding-left: 0.3rem;
            padding-right: 0.3rem;
        }

        .main-title {
            font-size: 1.25rem;
        }

        .sub-title {
            font-size: 0.65rem;
        }

        .score-value {
            font-size: 1.2rem;
        }

        .section-title {
            font-size: 0.9rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HELPERS
# =========================================================

def safe_float(value, default=0.0):

    try:

        if value is None:
            return default

        if pd.isna(value):
            return default

        return float(value)

    except Exception:

        return default


def display_value(value):

    if value is None:
        return "—"

    try:

        if pd.isna(value):
            return "—"

    except Exception:
        pass

    return value


def money_value(value):

    if value is None:
        return "—"

    try:

        if pd.isna(value):
            return "—"

        return f"₹{float(value):.2f}"

    except Exception:

        return "—"


def pct_value(value):

    if value is None:
        return "—"

    try:

        if pd.isna(value):
            return "—"

        return f"{float(value):.2f}%"

    except Exception:

        return "—"


# =========================================================
# ATR
# =========================================================

def calculate_atr(data, period=14):

    high = data["High"]
    low = data["Low"]
    close = data["Close"]

    previous_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - previous_close).abs()
    tr3 = (low - previous_close).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    return true_range.rolling(period).mean()


# =========================================================
# ADVANCED PRICE CHART
# =========================================================

def build_price_chart(
    symbol,
    cmp_value,
    stop_loss_value=None,
    swing_target_value=None,
    long_target_value=None
):

    symbol = str(symbol).strip().upper()

    ticker = (
        symbol
        if symbol.endswith(".NS")
        else f"{symbol}.NS"
    )

    try:

        data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if data.empty:

            st.warning(
                "📊 Chart માટે NSE historical data ઉપલબ્ધ નથી."
            )

            return


        # =================================================
        # MULTI INDEX FIX
        # =================================================

        if isinstance(
            data.columns,
            pd.MultiIndex
        ):

            data.columns = (
                data.columns
                .get_level_values(0)
            )


        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]


        for column in required_columns:

            if column not in data.columns:

                st.error(
                    f"Chart column missing: {column}"
                )

                return


        data = data[
            required_columns
        ].copy()


        # =================================================
        # NUMERIC CLEAN
        # =================================================

        for column in required_columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )


        data.dropna(
            subset=[
                "Open",
                "High",
                "Low",
                "Close"
            ],
            inplace=True
        )


        if len(data) < 30:

            st.warning(
                "📊 Chart માટે પૂરતો historical data નથી."
            )

            return


        # =================================================
        # EMA
        # =================================================

        data["EMA20"] = (
            data["Close"]
            .ewm(
                span=20,
                adjust=False
            )
            .mean()
        )


        data["EMA50"] = (
            data["Close"]
            .ewm(
                span=50,
                adjust=False
            )
            .mean()
        )


        data["EMA200"] = (
            data["Close"]
            .ewm(
                span=200,
                adjust=False
            )
            .mean()
        )


        # =================================================
        # ATR
        # =================================================

        atr_series = calculate_atr(
            data,
            14
        )

        atr_value = safe_float(
            atr_series.iloc[-1],
            0
        )


        current_price = safe_float(
            data["Close"].iloc[-1]
        )


        cmp = safe_float(
            cmp_value,
            current_price
        )


        # =================================================
        # TARGETS
        # =================================================

        if stop_loss_value is None:

            stop_loss = (
                cmp - 2 * atr_value
            )

        else:

            stop_loss = safe_float(
                stop_loss_value,
                cmp - 2 * atr_value
            )


        if swing_target_value is None:

            swing_target = (
                cmp + 2 * atr_value
            )

        else:

            swing_target = safe_float(
                swing_target_value,
                cmp + 2 * atr_value
            )


        if long_target_value is None:

            long_target = (
                cmp + 5 * atr_value
            )

        else:

            long_target = safe_float(
                long_target_value,
                cmp + 5 * atr_value
            )


        # =================================================
        # 52 WEEK
        # =================================================

        last_252 = data.tail(252)

        high_52 = safe_float(
            last_252["High"].max(),
            current_price
        )

        low_52 = safe_float(
            last_252["Low"].min(),
            current_price
        )


        # =================================================
        # FIGURE
        # =================================================

        fig = go.Figure()


        # =================================================
        # CANDLESTICK
        # =================================================

        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="PRICE"
            )
        )


        # =================================================
        # EMA 20
        # =================================================

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA20"],
                mode="lines",
                name="EMA 20",
                line=dict(
                    width=1.5
                )
            )
        )


        # =================================================
        # EMA 50
        # =================================================

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA50"],
                mode="lines",
                name="EMA 50",
                line=dict(
                    width=1.7
                )
            )
        )


        # =================================================
        # EMA 200
        # =================================================

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA200"],
                mode="lines",
                name="EMA 200",
                line=dict(
                    width=2
                )
            )
        )


        # =================================================
        # CMP
        # =================================================

        fig.add_hline(
            y=cmp,
            line_dash="solid",
            annotation_text=(
                f"CMP ₹{cmp:.2f}"
            ),
            annotation_position="right"
        )


        # =================================================
        # STOP LOSS
        # =================================================

        fig.add_hline(
            y=stop_loss,
            line_dash="dash",
            annotation_text=(
                f"SL ₹{stop_loss:.2f}"
            ),
            annotation_position="bottom right"
        )


        # =================================================
        # SWING
        # =================================================

        fig.add_hline(
            y=swing_target,
            line_dash="dot",
            annotation_text=(
                f"SWING ₹{swing_target:.2f}"
            ),
            annotation_position="top right"
        )


        # =================================================
        # LONG TARGET
        # =================================================

        fig.add_hline(
            y=long_target,
            line_dash="dot",
            annotation_text=(
                f"LONG ₹{long_target:.2f}"
            ),
            annotation_position="top left"
        )


        # =================================================
        # 52 WEEK HIGH
        # =================================================

        fig.add_hline(
            y=high_52,
            line_dash="dashdot",
            annotation_text=(
                f"52W HIGH ₹{high_52:.2f}"
            ),
            annotation_position="top"
        )


        # =================================================
        # 52 WEEK LOW
        # =================================================

        fig.add_hline(
            y=low_52,
            line_dash="dashdot",
            annotation_text=(
                f"52W LOW ₹{low_52:.2f}"
            ),
            annotation_position="bottom"
        )


        # =================================================
        # LAYOUT
        # =================================================

        fig.update_layout(

            height=600,

            hovermode="x unified",

            dragmode="pan",

            margin=dict(
                l=8,
                r=8,
                t=50,
                b=8
            ),

            showlegend=True,

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="center",
                x=0.5
            ),

            xaxis=dict(

                type="date",

                fixedrange=False,

                showgrid=True,

                rangeslider=dict(
                    visible=True,
                    thickness=0.07
                ),

                rangeselector=dict(

                    buttons=[

                        dict(
                            count=1,
                            label="1M",
                            step="month",
                            stepmode="backward"
                        ),

                        dict(
                            count=3,
                            label="3M",
                            step="month",
                            stepmode="backward"
                        ),

                        dict(
                            count=6,
                            label="6M",
                            step="month",
                            stepmode="backward"
                        ),

                        dict(
                            count=1,
                            label="1Y",
                            step="year",
                            stepmode="backward"
                        ),

                        dict(
                            step="all",
                            label="ALL"
                        )

                    ]

                )

            ),

            yaxis=dict(

                fixedrange=False,

                autorange=True,

                showgrid=True

            )

        )


        # =================================================
        # DISPLAY
        # =================================================

        st.plotly_chart(

            fig,

            use_container_width=True,

            config={

                "displaylogo": False,

                "responsive": True,

                "scrollZoom": True,

                "doubleClick": "reset",

                "displayModeBar": True

            },

            key=f"price_chart_{symbol}"

        )


        # =================================================
        # CHART SUMMARY
        # =================================================

        st.caption(
            f"📍 CMP ₹{cmp:.2f}  |  "
            f"🛑 SL ₹{stop_loss:.2f}  |  "
            f"🎯 Swing ₹{swing_target:.2f}  |  "
            f"🚀 Long ₹{long_target:.2f}"
        )


    except Exception as error:

        st.error(
            "📊 Price Chart Error: "
            f"{type(error).__name__}: {error}"
        )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    '📈 R.S MASTER STOCK GUIDE'
    '</div>',
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
# PORTFOLIO
# =========================================================

st.header("📁 પોર્ટફોલિયો")


try:

    portfolio = pd.read_csv(
        "portfolio.csv"
    )

except Exception as error:

    st.error(
        f"Portfolio loading error: {error}"
    )

    st.stop()


if portfolio.empty:

    st.warning(
        "પોર્ટફોલિયો ડેટા ઉપલબ્ધ નથી."
    )

    st.stop()


if "SYMBOL" not in portfolio.columns:

    st.error(
        "portfolio.csv માં SYMBOL column જરૂરી છે."
    )

    st.stop()


st.dataframe(
    portfolio,
    use_container_width=True,
    hide_index=True
)


st.divider()


# =========================================================
# SCORES
# =========================================================

all_scores = []


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

    result = fetch_nse_data(
        symbol
    )


    if result.get("STATUS") != "FRESH":

        st.error(
            f"{symbol}: NSE data unavailable — "
            f"{result.get('STATUS', '--')}"
        )

        continue


    # =====================================================
    # FUNDAMENTAL
    # =====================================================

    fundamental = (
        fetch_fundamental_data(
            symbol
        )
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

    master_score = round(

        technical_score * 0.40

        +

        fundamental_score * 0.40

        +

        risk_score * 0.20,

        1

    )


    # =====================================================
    # DECISION
    # =====================================================

    if master_score >= 75:

        decision = "BUY"

        decision_text = (
            "🟢 ખરીદી / વધારો"
        )

        decision_class = "green"


    elif master_score >= 60:

        decision = "HOLD"

        decision_text = (
            "🟢 જાળવો"
        )

        decision_class = "green"


    elif master_score >= 45:

        decision = "WAIT"

        decision_text = (
            "🟡 રાહ જુઓ"
        )

        decision_class = "yellow"


    elif master_score >= 30:

        decision = "REDUCE"

        decision_text = (
            "🟠 ઘટાડો"
        )

        decision_class = "orange"


    else:

        decision = "EXIT"

        decision_text = (
            "🔴 બહાર નીકળો"
        )

        decision_class = "red"


    # =====================================================
    # MARKET ZONE
    # =====================================================

    if master_score >= 75:

        market_zone = "🐂 BULL"


    elif master_score >= 55:

        market_zone = "🐷 PIG"


    else:

        market_zone = "🐻 BEAR"


    # =====================================================
    # PRICE
    # =====================================================

    cmp = safe_float(
        result.get(
            "CMP"
        )
    )


    atr = safe_float(
        result.get(
            "ATR_14"
        )
    )


    # =====================================================
    # STOP LOSS
    # =====================================================

    stop_loss = safe_float(
        result.get(
            "STOP_LOSS"
        ),
        cmp - (2 * atr)
    )


    # =====================================================
    # TARGETS
    # =====================================================

    swing_target = safe_float(

        result.get(
            "SWING_TARGET"
        ),

        cmp + (2 * atr)

    )


    long_term_target = safe_float(

        result.get(
            "LONG_TERM_TARGET"
        ),

        cmp + (5 * atr)

    )


    # =====================================================
    # MOMENTUM
    # =====================================================

    momentum_level = safe_float(

        result.get(
            "MOMENTUM_LEVEL"
        ),

        result.get(
            "EMA_20"
        )

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
    # BASIC
    # =====================================================

    c1, c2 = st.columns(2)


    with c1:

        st.metric(
            "CMP",
            money_value(
                cmp
            )
        )


    with c2:

        st.metric(
            "બદલાવ",
            pct_value(
                result.get(
                    "CHANGE_%"
                )
            )
        )


    st.metric(
        "Momentum Level",
        money_value(
            momentum_level
        )
    )


    # =====================================================
    # MASTER
    # =====================================================

    st.markdown(

        f"""
        <div class="score-card">
            <div class="score-title">
                🏦 MASTER SCORE
            </div>
            <div class="score-value">
                {master_score}/100
            </div>
        </div>

        <div class="decision-card {decision_class}">
            🎯 {decision_text}
        </div>

        <div class="decision-card blue">
            MARKET ZONE<br>
            {market_zone}
        </div>
        """,

        unsafe_allow_html=True

    )


    # =====================================================
    # TARGET
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '🎯 Target & Risk'
        '</div>',
        unsafe_allow_html=True
    )


    t1, t2, t3 = st.columns(3)


    with t1:

        st.metric(
            "Swing Target",
            money_value(
                swing_target
            )
        )


    with t2:

        st.metric(
            "Long-Term Target",
            money_value(
                long_term_target
            )
        )


    with t3:

        st.metric(
            "Common Stop Loss",
            money_value(
                stop_loss
            )
        )


    # =====================================================
    # DECISION MESSAGE
    # =====================================================

    if decision == "BUY":

        st.success(
            "🟢 Buy — Setup positive"
        )


    elif decision == "HOLD":

        st.info(
            "🟢 Hold — Setup stable"
        )


    elif decision == "WAIT":

        st.warning(
            "🟡 Wait — confirmation જરૂરી"
        )


    elif decision == "REDUCE":

        st.warning(
            "🟠 Reduce — risk/reward weak"
        )


    else:

        st.error(
            "🔴 Exit — setup weak"
        )


    # =====================================================
    # PRICE CHART
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '📊 Price Chart'
        '</div>',
        unsafe_allow_html=True
    )


    build_price_chart(

        symbol=symbol,

        cmp_value=cmp,

        stop_loss_value=stop_loss,

        swing_target_value=swing_target,

        long_target_value=long_term_target

    )


    # =====================================================
    # TECHNICAL
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '📈 ટેક્નિકલ'
        '</div>',
        unsafe_allow_html=True
    )


    tc1, tc2, tc3 = st.columns(3)


    tc1.metric(
        "Technical Score",
        f"{technical_score:.0f}/100"
    )


    tc2.metric(
        "Technical Zone",
        display_value(
            result.get(
                "TECHNICAL_ZONE"
            )
        )
    )


    tc3.metric(
        "RSI 14",
        display_value(
            result.get(
                "RSI_14"
            )
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
        money_value(
            result.get(
                "EMA_10"
            )
        )
    )


    e2.metric(
        "20",
        money_value(
            result.get(
                "EMA_20"
            )
        )
    )


    e3.metric(
        "50",
        money_value(
            result.get(
                "EMA_50"
            )
        )
    )


    e4.metric(
        "100",
        money_value(
            result.get(
                "EMA_100"
            )
        )
    )


    e5.metric(
        "200",
        money_value(
            result.get(
                "EMA_200"
            )
        )
    )


    st.caption(
        "EMA Alignment: "
        f"**{display_value(result.get('EMA_ALIGNMENT'))}**"
    )


    # =====================================================
    # MOMENTUM
    # =====================================================

    m1, m2, m3 = st.columns(3)


    m1.metric(
        "RSI",
        display_value(
            result.get(
                "RSI_14"
            )
        )
    )


    m2.metric(
        "MACD",
        display_value(
            result.get(
                "MACD"
            )
        )
    )


    m3.metric(
        "Histogram",
        display_value(
            result.get(
                "MACD_HIST"
            )
        )
    )


    # =====================================================
    # SUPERTREND
    # =====================================================

    s1, s2 = st.columns(2)


    s1.metric(
        "Supertrend",
        money_value(
            result.get(
                "SUPERTREND"
            )
        )
    )


    s2.metric(
        "Trend",
        display_value(
            result.get(
                "SUPERTREND_STATUS"
            )
        )
    )


    # =====================================================
    # VOLUME
    # =====================================================

    v1, v2, v3 = st.columns(3)


    v1.metric(
        "Volume",
        display_value(
            result.get(
                "VOLUME"
            )
        )
    )


    v2.metric(
        "Volume Ratio",
        f"{display_value(result.get('VOLUME_RATIO'))}x"
    )


    v3.metric(
        "Breakout",
        display_value(
            result.get(
                "VOLUME_BREAKOUT"
            )
        )
    )


    # =====================================================
    # FUNDAMENTAL
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '🏢 ફન્ડામેન્ટલ'
        '</div>',
        unsafe_allow_html=True
    )


    fc1, fc2, fc3 = st.columns(3)


    fc1.metric(
        "Fundamental Score",
        f"{fundamental_score:.0f}/100"
    )


    fc2.metric(
        "Zone",
        display_value(
            fundamental.get(
                "FUNDAMENTAL_ZONE"
            )
        )
    )


    fc3.metric(
        "Data Quality",
        pct_value(
            fundamental.get(
                "DATA_QUALITY_%"
            )
        )
    )


    f1, f2, f3 = st.columns(3)


    f1.metric(
        "Revenue Growth",
        pct_value(
            fundamental.get(
                "REVENUE_GROWTH_%"
            )
        )
    )


    f2.metric(
        "Profit Growth",
        pct_value(
            fundamental.get(
                "PROFIT_GROWTH_%"
            )
        )
    )


    f3.metric(
        "ROE",
        pct_value(
            fundamental.get(
                "ROE_%"
            )
        )
    )


    # =====================================================
    # RISK
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '🛡️ જોખમ'
        '</div>',
        unsafe_allow_html=True
    )


    r1, r2, r3 = st.columns(3)


    r1.metric(
        "Risk Score",
        f"{risk_score:.0f}/100"
    )


    r2.metric(
        "Risk Level",
        display_value(
            result.get(
                "RISK_LEVEL"
            )
        )
    )


    r3.metric(
        "Risk %",
        pct_value(
            result.get(
                "RISK_%"
            )
        )
    )


    # =====================================================
    # DATA
    # =====================================================

    st.caption(
        f"📅 Data Date: "
        f"{display_value(result.get('DATA_DATE'))}"
        f" | Status: "
        f"{display_value(result.get('STATUS'))}"
    )


    # =====================================================
    # COPY RESULT
    # =====================================================

    copy_text = f"""
R.S MASTER STOCK GUIDE

Stock: {symbol}
CMP: ₹{cmp:.2f}

MASTER SCORE: {master_score}/100
DECISION: {decision_text}
ZONE: {market_zone}

Technical Score: {technical_score:.0f}/100
Fundamental Score: {fundamental_score:.0f}/100
Risk Score: {risk_score:.0f}/100

Swing Target: ₹{swing_target:.2f}
Long-Term Target: ₹{long_term_target:.2f}
Common Stop Loss: ₹{stop_loss:.2f}

Momentum Level: ₹{momentum_level:.2f}

Technical Zone: {display_value(result.get("TECHNICAL_ZONE"))}
RSI: {display_value(result.get("RSI_14"))}
MACD: {display_value(result.get("MACD"))}
Supertrend: {display_value(result.get("SUPERTREND_STATUS"))}
Volume Breakout: {display_value(result.get("VOLUME_BREAKOUT"))}

Data Date: {display_value(result.get("DATA_DATE"))}
"""


    st.code(
        copy_text.strip(),
        language="text"
    )


    # =====================================================
    # STORE
    # =====================================================

    all_scores.append({

        "SYMBOL": symbol,

        "MASTER_SCORE": master_score,

        "DECISION": decision,

        "ZONE": market_zone

    })


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()


# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

st.header(
    "📊 પોર્ટફોલિયો સારાંશ"
)


if all_scores:

    scores_df = pd.DataFrame(
        all_scores
    )


    portfolio_health = round(

        scores_df[
            "MASTER_SCORE"
        ].mean(),

        1

    )


    buy_count = int(

        (
            scores_df["DECISION"]
            == "BUY"
        ).sum()

    )


    hold_count = int(

        (
            scores_df["DECISION"]
            == "HOLD"
        ).sum()

    )


    reduce_count = int(

        (
            scores_df["DECISION"]
            == "REDUCE"
        ).sum()

    )


    exit_count = int(

        (
            scores_df["DECISION"]
            == "EXIT"
        ).sum()

    )


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "Stocks",
        len(scores_df)
    )


    c2.metric(
        "Portfolio Health",
        f"{portfolio_health}/100"
    )


    c3.metric(
        "BUY / HOLD",
        f"{buy_count} / {hold_count}"
    )


    st.caption(
        f"REDUCE: {reduce_count} | "
        f"EXIT: {exit_count}"
    )


else:

    st.info(
        "Portfolio summary માટે data ઉપલબ્ધ નથી."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()


st.caption(
    "📈 R.S MASTER STOCK GUIDE | "
    "NSE Stock Decision System"
)
