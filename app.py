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
# MOBILE UI
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        padding-left: 0.4rem;
        padding-right: 0.4rem;
        max-width: 1200px;
    }

    .main-title {
        text-align: center;
        font-size: 1.55rem;
        font-weight: 900;
    }

    .sub-title {
        text-align: center;
        font-size: 0.75rem;
        opacity: 0.75;
        margin-bottom: 8px;
    }

    .stock-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 12px;
    }

    .score-card {
        text-align: center;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        padding: 12px;
    }

    .score-title {
        font-size: 0.7rem;
        opacity: 0.7;
        font-weight: 800;
    }

    .score-value {
        font-size: 1.4rem;
        font-weight: 900;
    }

    .decision-card {
        text-align: center;
        border-radius: 14px;
        padding: 10px;
        margin: 8px 0;
        font-weight: 900;
    }

    .green {
        background: rgba(0,180,80,0.12);
        border: 1px solid rgba(0,180,80,0.3);
    }

    .yellow {
        background: rgba(240,180,0,0.12);
        border: 1px solid rgba(240,180,0,0.3);
    }

    .orange {
        background: rgba(255,130,0,0.12);
        border: 1px solid rgba(255,130,0,0.3);
    }

    .red {
        background: rgba(220,40,40,0.12);
        border: 1px solid rgba(220,40,40,0.3);
    }

    .blue {
        background: rgba(40,120,220,0.12);
        border: 1px solid rgba(40,120,220,0.3);
    }

    .section-title {
        font-size: 1rem;
        font-weight: 900;
        margin-top: 10px;
        margin-bottom: 7px;
    }

    @media (max-width: 640px) {

        .block-container {
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }

        .main-title {
            font-size: 1.25rem;
        }

        .sub-title {
            font-size: 0.65rem;
        }

        .score-value {
            font-size: 1.15rem;
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


def money(value):

    try:

        if value is None or pd.isna(value):
            return "—"

        return f"₹{float(value):.2f}"

    except Exception:

        return "—"


def percent(value):

    try:

        if value is None or pd.isna(value):
            return "—"

        return f"{float(value):.2f}%"

    except Exception:

        return "—"


def show_value(value):

    try:

        if value is None or pd.isna(value):
            return "—"

    except Exception:
        pass

    return value


# =========================================================
# ATR
# =========================================================

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
# PRICE CHART
# =========================================================

# =========================================================
# 📊 ADVANCED PRICE CHART — CLEAN VERSION
# =========================================================

def build_price_chart(symbol):

    symbol = str(symbol).strip().upper()

    ticker = (
        symbol
        if symbol.endswith(".NS")
        else f"{symbol}.NS"
    )

    try:

        # -------------------------------------------------
        # DOWNLOAD HISTORICAL DATA
        # -------------------------------------------------

        chart_data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if chart_data is None or chart_data.empty:

            st.warning(
                "📊 Chart માટે historical NSE data ઉપલબ્ધ નથી."
            )

            return


        # -------------------------------------------------
        # MULTI INDEX FIX
        # -------------------------------------------------

        if isinstance(
            chart_data.columns,
            pd.MultiIndex
        ):

            chart_data.columns = (
                chart_data.columns
                .get_level_values(0)
            )


        required_columns = [
            "Open",
            "High",
            "Low",
            "Close"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in chart_data.columns
        ]

        if missing_columns:

            st.warning(
                "📊 Chart columns missing: "
                + ", ".join(missing_columns)
            )

            return


        chart_data = (
            chart_data[required_columns]
            .dropna()
            .copy()
        )


        if len(chart_data) < 30:

            st.warning(
                "📊 Chart માટે પૂરતો historical data નથી."
            )

            return


        # -------------------------------------------------
        # NUMERIC DATA
        # -------------------------------------------------

        for col in required_columns:

            chart_data[col] = pd.to_numeric(
                chart_data[col],
                errors="coerce"
            )

        chart_data = chart_data.dropna()


        # -------------------------------------------------
        # EMA
        # -------------------------------------------------

        close = chart_data["Close"]

        chart_data["EMA10"] = (
            close
            .ewm(
                span=10,
                adjust=False
            )
            .mean()
        )

        chart_data["EMA20"] = (
            close
            .ewm(
                span=20,
                adjust=False
            )
            .mean()
        )

        chart_data["EMA50"] = (
            close
            .ewm(
                span=50,
                adjust=False
            )
            .mean()
        )

        chart_data["EMA100"] = (
            close
            .ewm(
                span=100,
                adjust=False
            )
            .mean()
        )

        chart_data["EMA200"] = (
            close
            .ewm(
                span=200,
                adjust=False
            )
            .mean()
        )


        # -------------------------------------------------
        # CURRENT PRICE
        # -------------------------------------------------

        cmp = float(
            close.iloc[-1]
        )


        # -------------------------------------------------
        # ATR
        # -------------------------------------------------

        high = chart_data["High"]
        low = chart_data["Low"]

        previous_close = (
            close.shift(1)
        )

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

        atr = (
            true_range
            .rolling(14)
            .mean()
        )

        atr_value = float(
            atr.iloc[-1]
        )

        if pd.isna(atr_value) or atr_value <= 0:

            atr_value = cmp * 0.03


        # -------------------------------------------------
        # TARGET / RISK LEVELS
        # -------------------------------------------------

        stop_loss = (
            cmp - (2 * atr_value)
        )

        swing_target = (
            cmp + (2 * atr_value)
        )

        long_term_target = (
            cmp + (5 * atr_value)
        )

        high_52w = float(
            chart_data["High"].max()
        )

        low_52w = float(
            chart_data["Low"].min()
        )


        # -------------------------------------------------
        # PRICE CHART HEADER
        # -------------------------------------------------

        st.markdown(
            "### 📊 Price Chart"
        )

        st.caption(
            "🔍 Zoom • Pan • EMA • Target • Stop Loss • 52W Levels"
        )


        # -------------------------------------------------
        # FIGURE
        # -------------------------------------------------

        fig = go.Figure()


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

                increasing_fillcolor="#00C853",

                decreasing_line_color="#FF1744",

                decreasing_fillcolor="#FF1744"
            )
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

                line=dict(
                    width=1
                ),

                visible=True
            )
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

                line=dict(
                    width=1.2
                ),

                visible=True
            )
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

                line=dict(
                    width=1.5
                ),

                visible=True
            )
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

                line=dict(
                    width=1.5
                ),

                visible=False
            )
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

                line=dict(
                    width=2
                ),

                visible=False
            )
        )


        # -------------------------------------------------
        # CMP
        # -------------------------------------------------

        fig.add_hline(

            y=cmp,

            line_dash="dot",

            line_width=1,

            annotation_text=(
                f"CMP ₹{cmp:.2f}"
            ),

            annotation_position="top right"
        )


        # -------------------------------------------------
        # STOP LOSS
        # -------------------------------------------------

        fig.add_hline(

            y=stop_loss,

            line_dash="dash",

            line_width=1,

            annotation_text=(
                f"SL ₹{stop_loss:.2f}"
            ),

            annotation_position="bottom right"
        )


        # -------------------------------------------------
        # SWING TARGET
        # -------------------------------------------------

        fig.add_hline(

            y=swing_target,

            line_dash="dot",

            line_width=1,

            annotation_text=(
                f"SWING ₹{swing_target:.2f}"
            ),

            annotation_position="top left"
        )


        # -------------------------------------------------
        # LONG TERM TARGET
        # -------------------------------------------------

        fig.add_hline(

            y=long_term_target,

            line_dash="dot",

            line_width=1,

            annotation_text=(
                f"LONG ₹{long_term_target:.2f}"
            ),

            annotation_position="top left"
        )


        # -------------------------------------------------
        # 52W HIGH
        # -------------------------------------------------

        fig.add_hline(

            y=high_52w,

            line_dash="dashdot",

            line_width=1,

            annotation_text=(
                f"52W HIGH ₹{high_52w:.2f}"
            ),

            annotation_position="top"
        )


        # -------------------------------------------------
        # 52W LOW
        # -------------------------------------------------

        fig.add_hline(

            y=low_52w,

            line_dash="dashdot",

            line_width=1,

            annotation_text=(
                f"52W LOW ₹{low_52w:.2f}"
            ),

            annotation_position="bottom"
        )


        # -------------------------------------------------
        # RANGE BUTTONS
        # -------------------------------------------------

        range_buttons = [

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

            title=dict(
                text=f"📈 {symbol} — Interactive Chart",
                x=0.5,
                xanchor="center"
            ),

            height=600,

            template="plotly_dark",

            hovermode="x unified",

            dragmode="pan",

            margin=dict(
                l=8,
                r=8,
                t=65,
                b=10
            ),

            showlegend=True,

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),

            xaxis=dict(

                type="date",

                showgrid=True,

                rangeslider=dict(
                    visible=True,
                    thickness=0.07
                ),

                rangeselector=dict(
                    buttons=range_buttons
                ),

                fixedrange=False
            ),

            yaxis=dict(

                showgrid=True,

                fixedrange=False,

                autorange=True,

                side="right"
            )
        )


        # -------------------------------------------------
        # MOBILE / ZOOM CONFIG
        # -------------------------------------------------

        chart_config = {

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
        # DISPLAY
        # -------------------------------------------------

        st.plotly_chart(

            fig,

            use_container_width=True,

            config=chart_config,

            key=f"price_chart_{symbol}"
        )


        # -------------------------------------------------
        # CHART SUMMARY
        # -------------------------------------------------

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "CMP",
            f"₹{cmp:.2f}"
        )

        c2.metric(
            "Stop Loss",
            f"₹{stop_loss:.2f}"
        )

        c3.metric(
            "Swing",
            f"₹{swing_target:.2f}"
        )

        c4.metric(
            "Long Term",
            f"₹{long_term_target:.2f}"
        )


    except Exception as error:

        st.error(
            f"📊 Price Chart Error: "
            f"{type(error).__name__}: {error}"
        )


# =========================================================
# CALL PRICE CHART
# =========================================================

build_price_chart(symbol)


# =========================================================
# 📈 TECHNICAL
# =========================================================

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
        result.get("TECHNICAL_ZONE")
    )
)

tc3.metric(
    "RSI 14",
    display_value(
        result.get("RSI_14")
    )
)


# =========================================================
# 📊 EMA
# =========================================================

st.markdown(
    "#### 📊 EMA"
)

e1, e2, e3, e4, e5 = st.columns(5)

e1.metric(
    "EMA 10",
    money_value(
        result.get("EMA_10")
    )
)

e2.metric(
    "EMA 20",
    money_value(
        result.get("EMA_20")
    )
)

e3.metric(
    "EMA 50",
    money_value(
        result.get("EMA_50")
    )
)

e4.metric(
    "EMA 100",
    money_value(
        result.get("EMA_100")
    )
)

e5.metric(
    "EMA 200",
    money_value(
        result.get("EMA_200")
    )
)

st.caption(
    "EMA Alignment: "
    f"**{display_value(result.get('EMA_ALIGNMENT'))}**"
)


# =========================================================
# MOMENTUM
# =========================================================

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


        # -------------------------------------------------
        # MULTIINDEX FIX
        # -------------------------------------------------

        if isinstance(
            data.columns,
            pd.MultiIndex
        ):

            data.columns = [
                column[0]
                for column in data.columns
            ]


        # -------------------------------------------------
        # REQUIRED DATA
        # -------------------------------------------------

        required = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        missing = [
            x
            for x in required
            if x not in data.columns
        ]

        if missing:

            st.error(
                f"Chart data missing: {missing}"
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
                "📊 Chart માટે પૂરતો data નથી."
            )

            return


        # =================================================
        # EMA
        # =================================================

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


        # =================================================
        # CURRENT PRICE
        # =================================================

        cmp = safe_float(
            close.iloc[-1]
        )


        # =================================================
        # ATR
        # =================================================

        atr = calculate_atr(
            data,
            14
        )

        atr_value = safe_float(
            atr.iloc[-1]
        )


        # =================================================
        # LEVELS
        # =================================================

        stop_loss = (
            cmp - (2 * atr_value)
        )

        swing_target = (
            cmp + (2 * atr_value)
        )

        long_target = (
            cmp + (5 * atr_value)
        )

        high_52w = safe_float(
            data["High"].max()
        )

        low_52w = safe_float(
            data["Low"].min()
        )


        # =================================================
        # FIGURE
        # =================================================

        fig = go.Figure()


        # =================================================
        # CANDLE
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
        # EMA 10
        # =================================================

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA10"],
                mode="lines",
                name="EMA 10",
                line=dict(width=1)
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
                line=dict(width=1.2)
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
                line=dict(width=1.5)
            )
        )


        # =================================================
        # EMA 100
        # =================================================

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA100"],
                mode="lines",
                name="EMA 100",
                visible="legendonly",
                line=dict(width=1.5)
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
                visible="legendonly",
                line=dict(width=2)
            )
        )


        # =================================================
        # CMP
        # =================================================

        fig.add_hline(
            y=cmp,
            line_dash="dot",
            annotation_text=f"CMP ₹{cmp:.2f}"
        )


        # =================================================
        # STOP LOSS
        # =================================================

        fig.add_hline(
            y=stop_loss,
            line_dash="dash",
            annotation_text=f"SL ₹{stop_loss:.2f}"
        )


        # =================================================
        # SWING TARGET
        # =================================================

        fig.add_hline(
            y=swing_target,
            line_dash="dot",
            annotation_text=f"Swing ₹{swing_target:.2f}"
        )


        # =================================================
        # LONG TARGET
        # =================================================

        fig.add_hline(
            y=long_target,
            line_dash="dot",
            annotation_text=f"Long ₹{long_target:.2f}"
        )


        # =================================================
        # 52W HIGH
        # =================================================

        fig.add_hline(
            y=high_52w,
            line_dash="dashdot",
            annotation_text=f"52W High ₹{high_52w:.2f}"
        )


        # =================================================
        # 52W LOW
        # =================================================

        fig.add_hline(
            y=low_52w,
            line_dash="dashdot",
            annotation_text=f"52W Low ₹{low_52w:.2f}"
        )


        # =================================================
        # LAYOUT
        # =================================================

        fig.update_layout(

            title={
                "text":
                f"📈 {symbol} — Price Chart",
                "x": 0.5
            },

            height=600,

            template="plotly_dark",

            hovermode="x unified",

            dragmode="pan",

            margin={
                "l": 5,
                "r": 5,
                "t": 60,
                "b": 5
            },

            xaxis={
                "type": "date",
                "fixedrange": False,
                "rangeslider": {
                    "visible": True,
                    "thickness": 0.07
                },
                "rangeselector": {
                    "buttons": [
                        {
                            "count": 1,
                            "label": "1M",
                            "step": "month",
                            "stepmode": "backward"
                        },
                        {
                            "count": 3,
                            "label": "3M",
                            "step": "month",
                            "stepmode": "backward"
                        },
                        {
                            "count": 6,
                            "label": "6M",
                            "step": "month",
                            "stepmode": "backward"
                        },
                        {
                            "count": 1,
                            "label": "1Y",
                            "step": "year",
                            "stepmode": "backward"
                        },
                        {
                            "step": "all",
                            "label": "ALL"
                        }
                    ]
                }
            },

            yaxis={
                "fixedrange": False,
                "autorange": True,
                "showgrid": True
            },

            legend={
                "orientation": "h",
                "y": 1.02,
                "x": 0.5,
                "xanchor": "center"
            }
        )


        # =================================================
        # CHART CONFIG
        # =================================================

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


        # =================================================
        # DISPLAY
        # =================================================

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=config,
            key=f"chart_{symbol}"
        )


        st.caption(
            f"📍 CMP {money(cmp)} | "
            f"🛑 SL {money(stop_loss)} | "
            f"🎯 Swing {money(swing_target)} | "
            f"🎯 Long {money(long_target)}"
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
# STOCK ANALYSIS
# =========================================================

all_scores = []


for symbol in portfolio["SYMBOL"]:

    symbol = (
        str(symbol)
        .strip()
        .upper()
    )


    # =====================================================
    # NSE DATA
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

    fundamental = fetch_fundamental_data(
        symbol
    )

    if not isinstance(
        fundamental,
        dict
    ):

        fundamental = {}


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

        (
            technical_score * 0.40
            +
            fundamental_score * 0.40
            +
            risk_score * 0.20
        ),

        1
    )


    # =====================================================
    # DECISION
    # =====================================================

    if master_score >= 75:

        decision = "BUY"
        decision_text = "🟢 ખરીદી / વધારો"
        decision_class = "green"

    elif master_score >= 60:

        decision = "HOLD"
        decision_text = "🟢 જાળવો"
        decision_class = "green"

    elif master_score >= 45:

        decision = "WAIT"
        decision_text = "🟡 રાહ જુઓ"
        decision_class = "yellow"

    elif master_score >= 30:

        decision = "REDUCE"
        decision_text = "🟠 ઘટાડો"
        decision_class = "orange"

    else:

        decision = "EXIT"
        decision_text = "🔴 બહાર નીકળો"
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
        result.get("CMP")
    )

    atr = safe_float(
        result.get("ATR_14")
    )


    # =====================================================
    # STOP
    # =====================================================

    stop_loss = safe_float(
        result.get("STOP_LOSS"),
        cmp - (2 * atr)
    )


    # =====================================================
    # TARGET
    # =====================================================

    swing_target = safe_float(
        result.get("SWING_TARGET"),
        cmp + (2 * atr)
    )

    long_target = safe_float(
        result.get("LONG_TERM_TARGET"),
        cmp + (5 * atr)
    )


    # =====================================================
    # MOMENTUM
    # =====================================================

    momentum = safe_float(
        result.get("MOMENTUM_LEVEL"),
        safe_float(
            result.get("EMA_20"),
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


    # =====================================================
    # BASIC
    # =====================================================

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
                result.get(
                    "CHANGE_%"
                )
            )
        )


    st.metric(
        "Momentum Level",
        money(momentum)
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
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # ZONE
    # =====================================================

    st.markdown(
        f"""
        <div class="decision-card blue">
            MARKET ZONE<br>
            {market_zone}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # TARGET & RISK
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
            money(swing_target)
        )


    with t2:

        st.metric(
            "Long-Term Target",
            money(long_target)
        )


    with t3:

        st.metric(
            "Common Stop Loss",
            money(stop_loss)
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

    st.markdown(
        '<div class="section-title">'
        '📊 Price Chart'
        '</div>',
        unsafe_allow_html=True
    )

    build_price_chart(
        symbol
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
        show_value(
            result.get(
                "TECHNICAL_ZONE"
            )
        )
    )

    tc3.metric(
        "RSI 14",
        show_value(
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


    with e1:

        st.metric(
            "10",
            money(
                result.get(
                    "EMA_10"
                )
            )
        )


    with e2:

        st.metric(
            "20",
            money(
                result.get(
                    "EMA_20"
                )
            )
        )


    with e3:

        st.metric(
            "50",
            money(
                result.get(
                    "EMA_50"
                )
            )
        )


    with e4:

        st.metric(
            "100",
            money(
                result.get(
                    "EMA_100"
                )
            )
        )


    with e5:

        st.metric(
            "200",
            money(
                result.get(
                    "EMA_200"
                )
            )
        )


    st.caption(
        "EMA Alignment: "
        f"**{show_value(result.get('EMA_ALIGNMENT'))}**"
    )


    # =====================================================
    # MOMENTUM INDICATORS
    # =====================================================

    m1, m2, m3 = st.columns(3)


    m1.metric(
        "RSI",
        show_value(
            result.get(
                "RSI_14"
            )
        )
    )


    m2.metric(
        "MACD",
        show_value(
            result.get(
                "MACD"
            )
        )
    )


    m3.metric(
        "Histogram",
        show_value(
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
        money(
            result.get(
                "SUPERTREND"
            )
        )
    )


    s2.metric(
        "Trend",
        show_value(
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
        show_value(
            result.get(
                "VOLUME"
            )
        )
    )


    v2.metric(
        "Volume Ratio",
        f"{show_value(result.get('VOLUME_RATIO'))}x"
    )


    v3.metric(
        "Breakout",
        show_value(
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


    f1, f2, f3 = st.columns(3)


    f1.metric(
        "Fundamental Score",
        f"{fundamental_score:.0f}/100"
    )


    f2.metric(
        "Zone",
        show_value(
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


    f4, f5, f6 = st.columns(3)


    f4.metric(
        "Revenue Growth",
        percent(
            fundamental.get(
                "REVENUE_GROWTH_%"
            )
        )
    )


    f5.metric(
        "Profit Growth",
        percent(
            fundamental.get(
                "PROFIT_GROWTH_%"
            )
        )
    )


    f6.metric(
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
        f"{risk_score:.0f}/100"
    )


    r2.metric(
        "Risk Level",
        show_value(
            result.get(
                "RISK_LEVEL"
            )
        )
    )


    r3.metric(
        "Risk %",
        percent(
            result.get(
                "RISK_%"
            )
        )
    )


    # =====================================================
    # DATA DATE
    # =====================================================

    st.caption(
        f"📅 Data Date: "
        f"{show_value(result.get('DATA_DATE'))}"
        f" | Status: "
        f"{show_value(result.get('STATUS'))}"
    )


    # =====================================================
    # COPY RESULT
    # =====================================================

    copy_text = f"""
R.S MASTER STOCK GUIDE

Stock: {symbol}
CMP: ₹{cmp:.2f}

MASTER SCORE: {master_score}/100
DECISION: {decision}
ZONE: {market_zone}

Technical Score: {technical_score:.0f}/100
Fundamental Score: {fundamental_score:.0f}/100
Risk Score: {risk_score:.0f}/100

Swing Target: ₹{swing_target:.2f}
Long-Term Target: ₹{long_target:.2f}
Common Stop Loss: ₹{stop_loss:.2f}

Momentum Level: ₹{momentum:.2f}

Technical Zone: {show_value(result.get("TECHNICAL_ZONE"))}
RSI: {show_value(result.get("RSI_14"))}
MACD: {show_value(result.get("MACD"))}
Supertrend: {show_value(result.get("SUPERTREND_STATUS"))}
Volume Breakout: {show_value(result.get("VOLUME_BREAKOUT"))}

Data Date: {show_value(result.get("DATA_DATE"))}
"""


    st.code(
        copy_text.strip(),
        language="text"
    )


    # =====================================================
    # SCORE STORAGE
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

    scores = pd.DataFrame(
        all_scores
    )


    health = round(
        scores["MASTER_SCORE"].mean(),
        1
    )


    buy_count = int(
        (
            scores["DECISION"] == "BUY"
        ).sum()
    )


    hold_count = int(
        (
            scores["DECISION"] == "HOLD"
        ).sum()
    )


    reduce_count = int(
        (
            scores["DECISION"] == "REDUCE"
        ).sum()
    )


    exit_count = int(
        (
            scores["DECISION"] == "EXIT"
        ).sum()
    )


    p1, p2, p3 = st.columns(3)


    p1.metric(
        "Stocks",
        len(scores)
    )


    p2.metric(
        "Portfolio Health",
        f"{health}/100"
    )


    p3.metric(
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
