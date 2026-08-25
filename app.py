import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.nse_data import fetch_nse_data
from src.fundamental_engine import fetch_fundamental_data


# =========================================================
# PAGE
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

st.markdown(
    """
    <style>

    .block-container {
        padding: 0.45rem 0.35rem 1rem 0.35rem;
        max-width: 1250px;
    }

    .main-title {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 900;
        margin: 0;
    }

    .sub-title {
        text-align: center;
        font-size: 0.72rem;
        opacity: 0.7;
        margin-bottom: 0.5rem;
    }

    .stock-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 15px;
        background: rgba(128,128,128,0.035);
    }

    .score-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        padding: 12px;
        text-align: center;
    }

    .score-title {
        font-size: 0.7rem;
        font-weight: 800;
        opacity: 0.7;
    }

    .score-value {
        font-size: 1.45rem;
        font-weight: 900;
    }

    .decision {
        padding: 10px;
        border-radius: 13px;
        text-align: center;
        font-weight: 900;
        margin-top: 8px;
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
            padding: 0.25rem;
        }

        .main-title {
            font-size: 1.2rem;
        }

        .sub-title {
            font-size: 0.63rem;
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

    try:

        if value is None or pd.isna(value):
            return "—"

    except Exception:

        pass

    return value


def money(value):

    try:

        if value is None or pd.isna(value):
            return "—"

        return f"₹{float(value):,.2f}"

    except Exception:

        return "—"


def percent(value):

    try:

        if value is None or pd.isna(value):
            return "—"

        return f"{float(value):.2f}%"

    except Exception:

        return "—"


# =========================================================
# ATR
# =========================================================

def calculate_atr(data, period=14):

    high = pd.to_numeric(
        data["High"],
        errors="coerce"
    )

    low = pd.to_numeric(
        data["Low"],
        errors="coerce"
    )

    close = pd.to_numeric(
        data["Close"],
        errors="coerce"
    )

    previous = close.shift(1)

    tr_a = high - low
    tr_b = (high - previous).abs()
    tr_c = (low - previous).abs()

    true_range = pd.concat(
        [tr_a, tr_b, tr_c],
        axis=1
    ).max(axis=1)

    return true_range.rolling(
        period
    ).mean()


# =========================================================
# PRICE CHART
# =========================================================

def price_chart(
    symbol,
    stop_loss,
    swing_target,
    long_target
):

    st.markdown(
        "### 📊 Price Chart"
    )

    ticker = str(symbol).upper()

    if not ticker.endswith(".NS"):
        ticker = ticker + ".NS"

    try:

        data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

    except Exception as error:

        st.error(
            f"Chart data error: {error}"
        )

        return


    if data.empty:

        st.warning(
            "📊 Historical chart data મળ્યો નથી."
        )

        return


    # -----------------------------------------------------
    # MULTI INDEX
    # -----------------------------------------------------

    if isinstance(
        data.columns,
        pd.MultiIndex
    ):

        data.columns = [
            item[0]
            for item in data.columns
        ]


    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]


    for column in required:

        if column not in data.columns:

            st.warning(
                f"Chart column missing: {column}"
            )

            return


    data = data[
        required
    ].copy()


    for column in required:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )


    data = data.dropna()


    if len(data) < 30:

        st.warning(
            "Chart માટે historical data ઓછો છે."
        )

        return


    # -----------------------------------------------------
    # EMA
    # -----------------------------------------------------

    close = data["Close"]

    data["EMA10"] = close.ewm(
        span=10,
        adjust=False
    ).mean()

    data["EMA20"] = close.ewm(
        span=20,
        adjust=False
    ).mean()

    data["EMA50"] = close.ewm(
        span=50,
        adjust=False
    ).mean()

    data["EMA100"] = close.ewm(
        span=100,
        adjust=False
    ).mean()

    data["EMA200"] = close.ewm(
        span=200,
        adjust=False
    ).mean()


    # -----------------------------------------------------
    # 52 WEEK
    # -----------------------------------------------------

    high_52 = float(
        data["High"].max()
    )

    low_52 = float(
        data["Low"].min()
    )


    # -----------------------------------------------------
    # CURRENT
    # -----------------------------------------------------

    current_price = float(
        data["Close"].iloc[-1]
    )


    # =====================================================
    # CHART
    # =====================================================

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[
            0.80,
            0.20
        ]
    )


    # -----------------------------------------------------
    # CANDLE
    # -----------------------------------------------------

    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="PRICE"
        ),
        row=1,
        col=1
    )


    # -----------------------------------------------------
    # EMA
    # -----------------------------------------------------

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["EMA10"],
            name="EMA 10",
            mode="lines"
        ),
        row=1,
        col=1
    )


    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["EMA20"],
            name="EMA 20",
            mode="lines"
        ),
        row=1,
        col=1
    )


    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["EMA50"],
            name="EMA 50",
            mode="lines"
        ),
        row=1,
        col=1
    )


    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["EMA100"],
            name="EMA 100",
            mode="lines",
            visible="legendonly"
        ),
        row=1,
        col=1
    )


    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["EMA200"],
            name="EMA 200",
            mode="lines",
            visible="legendonly"
        ),
        row=1,
        col=1
    )


    # -----------------------------------------------------
    # VOLUME
    # -----------------------------------------------------

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="Volume"
        ),
        row=2,
        col=1
    )


    # =====================================================
    # LEVELS
    # =====================================================

    fig.add_hline(
        y=current_price,
        row=1,
        col=1,
        line_dash="dot",
        annotation_text=f"CMP ₹{current_price:,.2f}"
    )


    fig.add_hline(
        y=stop_loss,
        row=1,
        col=1,
        line_dash="dash",
        annotation_text=f"SL ₹{stop_loss:,.2f}"
    )


    fig.add_hline(
        y=swing_target,
        row=1,
        col=1,
        line_dash="dot",
        annotation_text=f"SWING ₹{swing_target:,.2f}"
    )


    fig.add_hline(
        y=long_target,
        row=1,
        col=1,
        line_dash="dot",
        annotation_text=f"LONG ₹{long_target:,.2f}"
    )


    fig.add_hline(
        y=high_52,
        row=1,
        col=1,
        line_dash="dashdot",
        annotation_text=f"52W HIGH ₹{high_52:,.2f}"
    )


    fig.add_hline(
        y=low_52,
        row=1,
        col=1,
        line_dash="dashdot",
        annotation_text=f"52W LOW ₹{low_52:,.2f}"
    )


    # =====================================================
    # TIME BUTTONS
    # =====================================================

    buttons = [

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


    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(
        height=650,
        template="plotly_dark",
        hovermode="x unified",
        dragmode="pan",
        margin=dict(
            l=5,
            r=5,
            t=70,
            b=5
        ),
        legend=dict(
            orientation="h",
            y=1.02,
            x=0.5,
            xanchor="center"
        )
    )


    # -----------------------------------------------------
    # X AXIS
    # -----------------------------------------------------

    fig.update_xaxes(
        type="date",
        rangeslider_visible=True,
        rangeselector_buttons=buttons,
        showgrid=False,
        row=1,
        col=1
    )


    fig.update_xaxes(
        type="date",
        showgrid=False,
        row=2,
        col=1
    )


    # -----------------------------------------------------
    # Y AXIS
    # -----------------------------------------------------

    fig.update_yaxes(
        autorange=True,
        showgrid=True,
        row=1,
        col=1
    )


    fig.update_yaxes(
        autorange=True,
        row=2,
        col=1
    )


    # =====================================================
    # MOBILE
    # =====================================================

    config = {
        "responsive": True,
        "scrollZoom": True,
        "doubleClick": "reset",
        "displaylogo": False,
        "displayModeBar": True
    }


    # =====================================================
    # DISPLAY
    # =====================================================

    st.plotly_chart(
        fig,
        use_container_width=True,
        config=config,
        key=f"chart_{symbol}"
    )


    st.caption(
        f"📍 CMP {money(current_price)} | "
        f"🛑 SL {money(stop_loss)} | "
        f"🎯 Swing {money(swing_target)} | "
        f"🚀 Long {money(long_target)}"
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
        f"portfolio.csv error: {error}"
    )

    st.stop()


if portfolio.empty:

    st.warning(
        "Portfolio ખાલી છે."
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
# RESULTS
# =========================================================

scores = []


for raw_symbol in portfolio["SYMBOL"]:

    symbol = str(
        raw_symbol
    ).strip().upper()


    # =====================================================
    # NSE
    # =====================================================

    try:

        result = fetch_nse_data(
            symbol
        )

    except Exception as error:

        st.error(
            f"{symbol}: NSE error — {error}"
        )

        continue


    if not isinstance(
        result,
        dict
    ):

        st.error(
            f"{symbol}: Invalid NSE result."
        )

        continue


    if result.get("STATUS") != "FRESH":

        st.error(
            f"{symbol}: Data not fresh."
        )

        continue


    # =====================================================
    # FUNDAMENTAL
    # =====================================================

    try:

        fundamental = fetch_fundamental_data(
            symbol
        )

    except Exception:

        fundamental = {}


    if not isinstance(
        fundamental,
        dict
    ):

        fundamental = {}


    # =====================================================
    # SCORES
    # =====================================================

    technical = safe_float(
        result.get(
            "TECHNICAL_SCORE"
        )
    )

    fundamental_score = safe_float(
        fundamental.get(
            "FUNDAMENTAL_SCORE"
        )
    )

    risk = safe_float(
        result.get(
            "RISK_SCORE"
        )
    )


    master = round(
        (
            technical * 0.40
            +
            fundamental_score * 0.40
            +
            risk * 0.20
        ),
        1
    )


    # =====================================================
    # DECISION
    # =====================================================

    if master >= 75:

        decision = "BUY"
        decision_text = "🟢 ખરીદી / વધારો"
        css = "green"

    elif master >= 60:

        decision = "HOLD"
        decision_text = "🟢 જાળવો"
        css = "green"

    elif master >= 45:

        decision = "WAIT"
        decision_text = "🟡 રાહ જુઓ"
        css = "yellow"

    elif master >= 30:

        decision = "REDUCE"
        decision_text = "🟠 ઘટાડો"
        css = "orange"

    else:

        decision = "EXIT"
        decision_text = "🔴 બહાર નીકળો"
        css = "red"


    # =====================================================
    # ZONE
    # =====================================================

    if master >= 75:

        zone = "🐂 BULL"

    elif master >= 55:

        zone = "🐷 PIG"

    else:

        zone = "🐻 BEAR"


    # =====================================================
    # PRICE
    # =====================================================

    cmp = safe_float(
        result.get("CMP")
    )

    atr = safe_float(
        result.get("ATR_14")
    )

    if atr <= 0:
        atr = max(
            cmp * 0.01,
            1
        )


    stop = safe_float(
        result.get("STOP_LOSS"),
        cmp - 2 * atr
    )

    swing = safe_float(
        result.get("SWING_TARGET"),
        cmp + 2 * atr
    )

    long_target = safe_float(
        result.get("LONG_TERM_TARGET"),
        cmp + 5 * atr
    )

    momentum = safe_float(
        result.get("MOMENTUM_LEVEL"),
        result.get("EMA_20", cmp)
    )


    # =====================================================
    # STOCK
    # =====================================================

    st.markdown(
        '<div class="stock-card">',
        unsafe_allow_html=True
    )


    st.subheader(
        f"📌 {symbol}"
    )


    c1, c2 = st.columns(2)


    with c1:

        st.metric(
            "CMP",
            money(cmp)
        )


    with c2:

        st.metric(
            "બદલાવ",
            percent(
                result.get("CHANGE_%")
            )
        )


    st.metric(
        "Momentum Level",
        money(momentum)
    )


    # =====================================================
    # SCORE
    # =====================================================

    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-title">
                🏦 MASTER SCORE
            </div>
            <div class="score-value">
                {master}/100
            </div>
        </div>

        <div class="decision {css}">
            🎯 {decision_text}
        </div>

        <div class="decision blue">
            MARKET ZONE<br>
            {zone}
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
            money(swing)
        )


    with t2:

        st.metric(
            "Long-Term Target",
            money(long_target)
        )


    with t3:

        st.metric(
            "Common Stop Loss",
            money(stop)
        )


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
    # CHART
    # =====================================================

    price_chart(
        symbol,
        stop,
        swing,
        long_target
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


    a, b, c = st.columns(3)


    a.metric(
        "Technical Score",
        f"{technical:.0f}/100"
    )


    b.metric(
        "Technical Zone",
        display_value(
            result.get(
                "TECHNICAL_ZONE"
            )
        )
    )


    c.metric(
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

    st.caption("📊 EMA")


    e1, e2, e3, e4, e5 = st.columns(5)


    e1.metric(
        "10",
        money(result.get("EMA_10"))
    )


    e2.metric(
        "20",
        money(result.get("EMA_20"))
    )


    e3.metric(
        "50",
        money(result.get("EMA_50"))
    )


    e4.metric(
        "100",
        money(result.get("EMA_100"))
    )


    e5.metric(
        "200",
        money(result.get("EMA_200"))
    )


    st.caption(
        "EMA Alignment: "
        f"**{display_value(result.get('EMA_ALIGNMENT'))}**"
    )


    # =====================================================
    # MACD
    # =====================================================

    m1, m2, m3 = st.columns(3)


    m1.metric(
        "RSI",
        display_value(
            result.get("RSI_14")
        )
    )


    m2.metric(
        "MACD",
        display_value(
            result.get("MACD")
        )
    )


    m3.metric(
        "Histogram",
        display_value(
            result.get("MACD_HIST")
        )
    )


    # =====================================================
    # SUPERTREND
    # =====================================================

    s1, s2 = st.columns(2)


    s1.metric(
        "Supertrend",
        money(
            result.get("SUPERTREND")
        )
    )


    s2.metric(
        "Trend",
        display_value(
            result.get("SUPERTREND_STATUS")
        )
    )


    # =====================================================
    # VOLUME
    # =====================================================

    v1, v2, v3 = st.columns(3)


    v1.metric(
        "Volume",
        display_value(
            result.get("VOLUME")
        )
    )


    v2.metric(
        "Volume Ratio",
        f"{display_value(result.get('VOLUME_RATIO'))}x"
    )


    v3.metric(
        "Breakout",
        display_value(
            result.get("VOLUME_BREAKOUT")
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


    f1, f2, f3 = st.columns(3)


    f1.metric(
        "Fundamental Score",
        f"{fundamental_score:.0f}/100"
    )


    f2.metric(
        "Zone",
        display_value(
            fundamental.get(
                "FUNDAMENTAL_ZONE"
            )
        )
    )


    f3.metric(
        "Data Quality",
        percent(
            fundamental.get(
                "DATA_QUALITY_%"
            )
        )
    )


    g1, g2, g3 = st.columns(3)


    g1.metric(
        "Revenue Growth",
        percent(
            fundamental.get(
                "REVENUE_GROWTH_%"
            )
        )
    )


    g2.metric(
        "Profit Growth",
        percent(
            fundamental.get(
                "PROFIT_GROWTH_%"
            )
        )
    )


    g3.metric(
        "ROE",
        percent(
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
        f"{risk:.0f}/100"
    )


    r2.metric(
        "Risk Level",
        display_value(
            result.get("RISK_LEVEL")
        )
    )


    r3.metric(
        "Risk %",
        percent(
            result.get("RISK_%")
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
    # COPY
    # =====================================================

    copy_text = f"""
R.S MASTER STOCK GUIDE

Stock: {symbol}
CMP: ₹{cmp:.2f}

MASTER SCORE: {master}/100
DECISION: {decision_text}
ZONE: {zone}

Technical Score: {technical:.0f}/100
Fundamental Score: {fundamental_score:.0f}/100
Risk Score: {risk:.0f}/100

Swing Target: ₹{swing:.2f}
Long-Term Target: ₹{long_target:.2f}
Common Stop Loss: ₹{stop:.2f}

Momentum Level: ₹{momentum:.2f}

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

    scores.append(
        {
            "SYMBOL": symbol,
            "MASTER_SCORE": master,
            "DECISION": decision,
            "ZONE": zone
        }
    )


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


if scores:

    df = pd.DataFrame(
        scores
    )


    health = round(
        df["MASTER_SCORE"].mean(),
        1
    )


    buy = int(
        (
            df["DECISION"] == "BUY"
        ).sum()
    )


    hold = int(
        (
            df["DECISION"] == "HOLD"
        ).sum()
    )


    reduce = int(
        (
            df["DECISION"] == "REDUCE"
        ).sum()
    )


    exit_count = int(
        (
            df["DECISION"] == "EXIT"
        ).sum()
    )


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "Stocks",
        len(df)
    )


    c2.metric(
        "Portfolio Health",
        f"{health}/100"
    )


    c3.metric(
        "BUY / HOLD",
        f"{buy} / {hold}"
    )


    st.caption(
        f"REDUCE: {reduce} | "
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
