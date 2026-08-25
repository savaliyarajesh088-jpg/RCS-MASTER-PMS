import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
# MOBILE / UI CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 0.55rem;
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
        font-size: 0.75rem;
        opacity: 0.72;
        margin-bottom: 0.55rem;
    }

    .stock-card {
        border: 1px solid rgba(128,128,128,0.24);
        border-radius: 16px;
        padding: 12px;
        margin-top: 8px;
        margin-bottom: 14px;
        background: rgba(128,128,128,0.035);
    }

    .score-card {
        border-radius: 14px;
        padding: 11px;
        text-align: center;
        border: 1px solid rgba(128,128,128,0.24);
        background: rgba(128,128,128,0.05);
    }

    .score-title {
        font-size: 0.68rem;
        opacity: 0.7;
        font-weight: 800;
    }

    .score-value {
        font-size: 1.45rem;
        font-weight: 900;
    }

    .decision-card {
        border-radius: 13px;
        padding: 10px;
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
        margin-top: 10px;
        margin-bottom: 7px;
    }

    @media (max-width: 640px) {

        .block-container {
            padding-left: 0.3rem;
            padding-right: 0.3rem;
            padding-top: 0.3rem;
        }

        .main-title {
            font-size: 1.25rem;
        }

        .sub-title {
            font-size: 0.66rem;
        }

        .score-value {
            font-size: 1.18rem;
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
    try:
        if value is None or pd.isna(value):
            return "—"
    except Exception:
        pass

    return value


def pct_value(value):
    try:
        if value is None or pd.isna(value):
            return "—"

        return f"{float(value):.2f}%"

    except Exception:
        return "—"


def money_value(value):
    try:
        if value is None or pd.isna(value):
            return "—"

        return f"₹{float(value):,.2f}"

    except Exception:
        return "—"


def calculate_atr(df, period=14):

    high = pd.to_numeric(
        df["High"],
        errors="coerce"
    )

    low = pd.to_numeric(
        df["Low"],
        errors="coerce"
    )

    close = pd.to_numeric(
        df["Close"],
        errors="coerce"
    )

    previous_close = close.shift(1)

    tr1 = high - low

    tr2 = (
        high - previous_close
    ).abs()

    tr3 = (
        low - previous_close
    ).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    return true_range.rolling(
        period
    ).mean()


# =========================================================
# ADVANCED MOBILE PRICE CHART
# =========================================================

def build_price_chart(
    symbol,
    stop_loss=None,
    swing_target=None,
    long_term_target=None
):

    symbol = str(symbol).strip().upper()

    ticker = (
        symbol
        if symbol.endswith(".NS")
        else symbol + ".NS"
    )

    st.markdown(
        "### 📊 Price Chart"
    )

    try:

        chart_data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if chart_data.empty:
            st.warning(
                "📊 Chart માટે historical NSE data ઉપલબ્ધ નથી."
            )
            return

        # -------------------------------------------------
        # MULTI INDEX PROTECTION
        # -------------------------------------------------

        if isinstance(
            chart_data.columns,
            pd.MultiIndex
        ):

            chart_data.columns = [
                column[0]
                for column in chart_data.columns
            ]

        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        missing = [
            column
            for column in required_columns
            if column not in chart_data.columns
        ]

        if missing:
            st.warning(
                "Chart columns missing: "
                + ", ".join(missing)
            )
            return

        chart_data = chart_data[
            required_columns
        ].copy()

        for column in required_columns:

            chart_data[column] = pd.to_numeric(
                chart_data[column],
                errors="coerce"
            )

        chart_data = chart_data.dropna()

        if len(chart_data) < 30:
            st.warning(
                "📊 Chart માટે પૂરતો historical data નથી."
            )
            return

        # -------------------------------------------------
        # EMA
        # -------------------------------------------------

        close = chart_data["Close"]

        chart_data["EMA10"] = (
            close.ewm(
                span=10,
                adjust=False
            ).mean()
        )

        chart_data["EMA20"] = (
            close.ewm(
                span=20,
                adjust=False
            ).mean()
        )

        chart_data["EMA50"] = (
            close.ewm(
                span=50,
                adjust=False
            ).mean()
        )

        chart_data["EMA100"] = (
            close.ewm(
                span=100,
                adjust=False
            ).mean()
        )

        chart_data["EMA200"] = (
            close.ewm(
                span=200,
                adjust=False
            ).mean()
        )

        # -------------------------------------------------
        # CURRENT VALUES
        # -------------------------------------------------

        cmp = float(
            close.iloc[-1]
        )

        atr_series = calculate_atr(
            chart_data,
            14
        )

        atr_series = atr_series.dropna()

        if atr_series.empty:

            atr_value = (
                abs(
                    float(
                        chart_data["High"].iloc[-1]
                    )
                    -
                    float(
                        chart_data["Low"].iloc[-1]
                    )
                )
            )

        else:

            atr_value = float(
                atr_series.iloc[-1]
            )

        if stop_loss is None:
            stop_loss = cmp - (
                2 * atr_value
            )

        if swing_target is None:
            swing_target = cmp + (
                2 * atr_value
            )

        if long_term_target is None:
            long_term_target = cmp + (
                5 * atr_value
            )

        stop_loss = safe_float(
            stop_loss,
            cmp - 2 * atr_value
        )

        swing_target = safe_float(
            swing_target,
            cmp + 2 * atr_value
        )

        long_term_target = safe_float(
            long_term_target,
            cmp + 5 * atr_value
        )

        # -------------------------------------------------
        # 52 WEEK LEVELS
        # -------------------------------------------------

        high_52w = float(
            chart_data["High"].max()
        )

        low_52w = float(
            chart_data["Low"].min()
        )

        # -------------------------------------------------
        # SUBTITLE
        # -------------------------------------------------

        st.caption(
            "🤏 Mobile: pinch zoom • drag to move • "
            "double tap reset • timeframe buttons available"
        )

        # -------------------------------------------------
        # FIGURE
        # -------------------------------------------------

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.025,
            row_heights=[
                0.78,
                0.22
            ]
        )

        # -------------------------------------------------
        # CANDLESTICK
        # -------------------------------------------------

        fig.add_trace(
            go.Candlestick(
                x=chart_data.index,
                open=chart_data["Open"],
                high=chart_data["High"],
                low=chart_data["Low"],
                close=chart_data["Close"],
                name="PRICE",
                increasing_line_color="#00C853",
                decreasing_line_color="#FF1744",
                increasing_fillcolor="#00C853",
                decreasing_fillcolor="#FF1744"
            ),
            row=1,
            col=1
        )

        # -------------------------------------------------
        # EMA 10
        # -------------------------------------------------

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["EMA10"],
                name="EMA 10",
                mode="lines",
                line=dict(width=1.2),
                visible=True
            ),
            row=1,
            col=1
        )

        # -------------------------------------------------
        # EMA 20
        # -------------------------------------------------

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["EMA20"],
                name="EMA 20",
                mode="lines",
                line=dict(width=1.2),
                visible=True
            ),
            row=1,
            col=1
        )

        # -------------------------------------------------
        # EMA 50
        # -------------------------------------------------

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["EMA50"],
                name="EMA 50",
                mode="lines",
                line=dict(width=1.5),
                visible=True
            ),
            row=1,
            col=1
        )

        # -------------------------------------------------
        # EMA 100
        # -------------------------------------------------

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["EMA100"],
                name="EMA 100",
                mode="lines",
                line=dict(width=1.5),
                visible=False
            ),
            row=1,
            col=1
        )

        # -------------------------------------------------
        # EMA 200
        # -------------------------------------------------

        fig.add_trace(
            go.Scatter(
                x=chart_data.index,
                y=chart_data["EMA200"],
                name="EMA 200",
                mode="lines",
                line=dict(width=2),
                visible=False
            ),
            row=1,
            col=1
        )

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        fig.add_trace(
            go.Bar(
                x=chart_data.index,
                y=chart_data["Volume"],
                name="Volume",
                opacity=0.55
            ),
            row=2,
            col=1
        )

        # -------------------------------------------------
        # CMP
        # -------------------------------------------------

        fig.add_hline(
            y=cmp,
            row=1,
            col=1,
            line_dash="dot",
            line_width=1,
            annotation_text=f"CMP ₹{cmp:,.2f}",
            annotation_position="top right"
        )

        # -------------------------------------------------
        # STOP LOSS
        # -------------------------------------------------

        fig.add_hline(
            y=stop_loss,
            row=1,
            col=1,
            line_dash="dash",
            line_width=1,
            annotation_text=f"SL ₹{stop_loss:,.2f}",
            annotation_position="bottom right"
        )

        # -------------------------------------------------
        # SWING TARGET
        # -------------------------------------------------

        fig.add_hline(
            y=swing_target,
            row=1,
            col=1,
            line_dash="dot",
            line_width=1,
            annotation_text=f"SWING ₹{swing_target:,.2f}",
            annotation_position="top left"
        )

        # -------------------------------------------------
        # LONG TERM TARGET
        # -------------------------------------------------

        fig.add_hline(
            y=long_term_target,
            row=1,
            col=1,
            line_dash="dot",
            line_width=1,
            annotation_text=f"LONG ₹{long_term_target:,.2f}",
            annotation_position="top left"
        )

        # -------------------------------------------------
        # 52 WEEK HIGH
        # -------------------------------------------------

        fig.add_hline(
            y=high_52w,
            row=1,
            col=1,
            line_dash="dashdot",
            line_width=1,
            annotation_text=f"52W HIGH ₹{high_52w:,.2f}",
            annotation_position="top"
        )

        # -------------------------------------------------
        # 52 WEEK LOW
        # -------------------------------------------------

        fig.add_hline(
            y=low_52w,
            row=1,
            col=1,
            line_dash="dashdot",
            line_width=1,
            annotation_text=f"52W LOW ₹{low_52w:,.2f}",
            annotation_position="bottom"
        )

        # -------------------------------------------------
        # TIMEFRAME BUTTONS
        # -------------------------------------------------

        timeframe_buttons = [

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

        # -------------------------------------------------
        # LAYOUT
        # -------------------------------------------------

        fig.update_layout(
            height=650,
            template="plotly_dark",
            hovermode="x unified",
            dragmode="pan",
            margin=dict(
                l=5,
                r=5,
                t=55,
                b=5
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
                rangeslider=dict(
                    visible=True,
                    thickness=0.06
                ),
                rangeselector=dict(
                    buttons=timeframe_buttons
                ),
                fixedrange=False
            ),
            xaxis2=dict(
                type="date",
                fixedrange=False
            ),
            yaxis=dict(
                fixedrange=False,
                autorange=True,
                fixedrange=False
            ),
            yaxis2=dict(
                fixedrange=False,
                autorange=True,
                fixedrange=False
            )
        )

        # -------------------------------------------------
        # MOBILE / DESKTOP CONTROLS
        # -------------------------------------------------

        config = {
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": True,
            "doubleClick": "reset",
            "displayModeBar": True,
            "modeBarButtonsToRemove": [
                "lasso2d",
                "select2d"
            ]
        }

        # -------------------------------------------------
        # SHOW CHART
        # -------------------------------------------------

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=config,
            key=f"price_chart_{symbol}"
        )

        # -------------------------------------------------
        # CHART SUMMARY
        # -------------------------------------------------

        st.caption(
            f"📍 CMP {money_value(cmp)}  |  "
            f"🛑 SL {money_value(stop_loss)}  |  "
            f"🎯 Swing {money_value(swing_target)}  |  "
            f"🚀 Long {money_value(long_term_target)}"
        )

    except Exception as error:

        st.error(
            f"📊 Chart Error: "
            f"{type(error).__name__}: {error}"
        )


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

    portfolio = pd.DataFrame()


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
# STOCK PROCESSING
# =========================================================

all_scores = []


for raw_symbol in portfolio["SYMBOL"]:

    symbol = str(
        raw_symbol
    ).strip().upper()

    # -----------------------------------------------------
    # NSE DATA
    # -----------------------------------------------------

    try:

        result = fetch_nse_data(
            symbol
        )

    except Exception as error:

        st.error(
            f"{symbol}: NSE engine error — {error}"
        )

        continue


    if not isinstance(
        result,
        dict
    ):

        st.error(
            f"{symbol}: NSE data format invalid."
        )

        continue


    if result.get("STATUS") != "FRESH":

        st.error(
            f"{symbol}: NSE data unavailable — "
            f"{result.get('STATUS', '--')}"
        )

        continue


    # -----------------------------------------------------
    # FUNDAMENTAL DATA
    # -----------------------------------------------------

    try:

        fundamental = (
            fetch_fundamental_data(
                symbol
            )
        )

    except Exception as error:

        fundamental = {
            "FUNDAMENTAL_SCORE": 0,
            "FUNDAMENTAL_ZONE": "POOR",
            "DATA_QUALITY_%": 0,
            "ERROR": str(error)
        }


    if not isinstance(
        fundamental,
        dict
    ):

        fundamental = {}


    # -----------------------------------------------------
    # SCORES
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # MASTER SCORE
    # -----------------------------------------------------

    master_score = round(
        (
            technical_score * 0.40
            +
            fundamental_score * 0.40
            +
            risk_score * 0.20
        ),
        1
    )


    # -----------------------------------------------------
    # DECISION
    # -----------------------------------------------------

    if master_score >= 75:

        decision = "BUY"

        decision_gujarati = (
            "🟢 ખરીદી / વધારો"
        )

        decision_class = "green"

    elif master_score >= 60:

        decision = "HOLD"

        decision_gujarati = (
            "🟢 જાળવો"
        )

        decision_class = "green"

    elif master_score >= 45:

        decision = "WAIT"

        decision_gujarati = (
            "🟡 રાહ જુઓ"
        )

        decision_class = "yellow"

    elif master_score >= 30:

        decision = "REDUCE"

        decision_gujarati = (
            "🟠 ઘટાડો"
        )

        decision_class = "orange"

    else:

        decision = "EXIT"

        decision_gujarati = (
            "🔴 બહાર નીકળો"
        )

        decision_class = "red"


    # -----------------------------------------------------
    # MARKET ZONE
    # -----------------------------------------------------

    if master_score >= 75:

        market_zone = "🐂 BULL"

    elif master_score >= 55:

        market_zone = "🐷 PIG"

    else:

        market_zone = "🐻 BEAR"


    # -----------------------------------------------------
    # PRICE / ATR
    # -----------------------------------------------------

    cmp = safe_float(
        result.get("CMP")
    )

    atr = safe_float(
        result.get("ATR_14")
    )

    stop_loss = safe_float(
        result.get(
            "STOP_LOSS"
        ),
        cmp - (
            2 * atr
        )
    )

    swing_target = safe_float(
        result.get(
            "SWING_TARGET"
        ),
        cmp + (
            2 * atr
        )
    )

    long_term_target = safe_float(
        result.get(
            "LONG_TERM_TARGET"
        ),
        cmp + (
            5 * atr
        )
    )

    momentum_level = safe_float(
        result.get(
            "MOMENTUM_LEVEL"
        ),
        safe_float(
            result.get(
                "EMA_20"
            ),
            cmp
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


    # -----------------------------------------------------
    # BASIC PRICE
    # -----------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "CMP",
            money_value(cmp)
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


    # -----------------------------------------------------
    # MOMENTUM
    # -----------------------------------------------------

    st.metric(
        "Momentum Level",
        money_value(
            momentum_level
        )
    )


    # -----------------------------------------------------
    # MASTER SCORE
    # -----------------------------------------------------

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
            🎯 {decision_gujarati}
        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # MARKET ZONE
    # -----------------------------------------------------

    st.markdown(
        f"""
        <div class="decision-card blue">
            MARKET ZONE<br>
            {market_zone}
        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # TARGET & RISK
    # -----------------------------------------------------

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

    build_price_chart(
        symbol=symbol,
        stop_loss=stop_loss,
        swing_target=swing_target,
        long_term_target=long_term_target
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


    # -----------------------------------------------------
    # EMA
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # MOMENTUM
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # SUPERTREND
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # VOLUME
    # -----------------------------------------------------

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


    rc1, rc2, rc3 = st.columns(3)

    rc1.metric(
        "Risk Score",
        f"{risk_score:.0f}/100"
    )

    rc2.metric(
        "Risk Level",
        display_value(
            result.get(
                "RISK_LEVEL"
            )
        )
    )

    rc3.metric(
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
DECISION: {decision_gujarati}
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
    # STORE SCORE
    # =====================================================

    all_scores.append(
        {
            "SYMBOL": symbol,
            "MASTER_SCORE": master_score,
            "DECISION": decision,
            "ZONE": market_zone
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
            scores_df[
                "DECISION"
            ] == "BUY"
        ).sum()
    )

    hold_count = int(
        (
            scores_df[
                "DECISION"
            ] == "HOLD"
        ).sum()
    )

    reduce_count = int(
        (
            scores_df[
                "DECISION"
            ] == "REDUCE"
        ).sum()
    )

    exit_count = int(
        (
            scores_df[
                "DECISION"
            ] == "EXIT"
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
