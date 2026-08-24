import streamlit as st
import pandas as pd


from src.nse_data import fetch_nse_data
from src.fundamental_engine import fetch_fundamental_data


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RCS MASTER PMS",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# MOBILE + COLOUR UI
# =========================================================

st.markdown(
    """
    <style>

    /* Main width */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        max-width: 1100px;
    }

    /* Header */
    .main-title {
        text-align: center;
        font-size: 1.65rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .sub-title {
        text-align: center;
        font-size: 0.85rem;
        opacity: 0.75;
        margin-bottom: 1rem;
    }

    /* Stock Card */
    .stock-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        padding: 14px;
        margin-top: 12px;
        margin-bottom: 16px;
        background: rgba(128,128,128,0.04);
    }

    /* Score Card */
    .score-card {
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        border: 1px solid rgba(128,128,128,0.25);
        background: rgba(128,128,128,0.05);
    }

    .score-title {
        font-size: 0.72rem;
        opacity: 0.7;
        font-weight: 700;
    }

    .score-value {
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 2px;
    }

    .decision-card {
        border-radius: 14px;
        padding: 13px;
        text-align: center;
        font-size: 1.15rem;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 10px;
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
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 6px;
    }

    .mini-label {
        font-size: 0.72rem;
        opacity: 0.7;
    }

    .mini-value {
        font-size: 0.95rem;
        font-weight: 700;
    }

    /* Mobile */
    @media (max-width: 640px) {

        .block-container {
            padding-left: 0.45rem;
            padding-right: 0.45rem;
            padding-top: 0.5rem;
        }

        .main-title {
            font-size: 1.35rem;
        }

        .sub-title {
            font-size: 0.72rem;
        }

        .score-value {
            font-size: 1.2rem;
        }

        .section-title {
            font-size: 0.92rem;
        }

        div[data-testid="stMetric"] {
            padding: 3px;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.68rem;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🏦 RCS MASTER PMS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'પોર્ટફોલિયો સમીક્ષા અને સંપત્તિ વૃદ્ધિ સિસ્ટમ'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# PORTFOLIO
# =========================================================

st.header("📁 પોર્ટફોલિયો")

try:

    portfolio = pd.read_csv("portfolio.csv")

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


# Compact portfolio table
st.dataframe(
    portfolio,
    use_container_width=True,
    hide_index=True
)

st.divider()


# =========================================================
# NSE + TECHNICAL
# =========================================================

st.header("📈 NSE અને ટેક્નિકલ વિશ્લેષણ")


for symbol in portfolio["SYMBOL"]:

    symbol = str(symbol).strip().upper()

    # =====================================================
    # NSE DATA
    # =====================================================

    result = fetch_nse_data(symbol)

    st.markdown(
        '<div class="stock-card">',
        unsafe_allow_html=True
    )

    st.subheader(f"📌 {symbol}")

    if result.get("STATUS") != "FRESH":

        st.error(
            f"NSE ડેટા ઉપલબ્ધ નથી: "
            f"{result.get('STATUS', '--')}"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        continue


    # =====================================================
    # BASIC PRICE
    # =====================================================

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "CMP",
            f"₹{result.get('CMP', '--')}"
        )

    with c2:

        st.metric(
            "બદલાવ %",
            f"{result.get('CHANGE_%', '--')}%"
        )


    # =====================================================
    # PMS MASTER SCORE
    # =====================================================

    technical_score = result.get(
        "TECHNICAL_SCORE",
        0
    )

    fundamental = fetch_fundamental_data(symbol)

    fundamental_score = fundamental.get(
        "FUNDAMENTAL_SCORE",
        0
    )

    risk_score = result.get(
        "RISK_SCORE",
        0
    )


    # Safe numeric conversion
    try:
        technical_score_num = float(
            technical_score
        )
    except:
        technical_score_num = 0


    try:
        fundamental_score_num = float(
            fundamental_score
        )
    except:
        fundamental_score_num = 0


    try:
        risk_score_num = float(
            risk_score
        )
    except:
        risk_score_num = 0


    # PMS calculation
    pms_score = (
        technical_score_num * 0.40
        +
        fundamental_score_num * 0.40
        +
        risk_score_num * 0.20
    )

    pms_score = round(
        pms_score,
        1
    )


    # =====================================================
    # CIO DECISION
    # =====================================================

    if pms_score >= 75:

        cio_decision = "BUY"
        decision_gujarati = "🟢 ખરીદી / વધારો"
        decision_class = "green"

    elif pms_score >= 60:

        cio_decision = "HOLD"
        decision_gujarati = "🟢 જાળવો"
        decision_class = "green"

    elif pms_score >= 45:

        cio_decision = "WAIT"
        decision_gujarati = "🟡 રાહ જુઓ"
        decision_class = "yellow"

    elif pms_score >= 30:

        cio_decision = "REDUCE"
        decision_gujarati = "🟠 ઘટાડો"
        decision_class = "orange"

    else:

        cio_decision = "EXIT"
        decision_gujarati = "🔴 બહાર નીકળો"
        decision_class = "red"


    # =====================================================
    # PMS CARD
    # =====================================================

    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-title">
                🏦 PMS MASTER SCORE
            </div>
            <div class="score-value">
                {pms_score}/100
            </div>
        </div>

        <div class="decision-card {decision_class}">
            🎯 મુખ્ય રોકાણ નિર્ણય<br>
            {decision_gujarati}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # TECHNICAL
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '📈 ટેક્નિકલ વિશ્લેષણ'
        '</div>',
        unsafe_allow_html=True
    )

    t1, t2, t3 = st.columns(3)

    t1.metric(
        "સ્કોર",
        f"{technical_score_num:.0f}/100"
    )

    t2.metric(
        "ઝોન",
        result.get(
            "TECHNICAL_ZONE",
            "--"
        )
    )

    t3.metric(
        "RSI 14",
        result.get(
            "RSI_14",
            "--"
        )
    )


    # =====================================================
    # EMA
    # =====================================================

    st.caption("📊 EMA")

    e1, e2, e3, e4, e5 = st.columns(5)

    e1.metric(
        "10",
        f"₹{result.get('EMA_10', '--')}"
    )

    e2.metric(
        "20",
        f"₹{result.get('EMA_20', '--')}"
    )

    e3.metric(
        "50",
        f"₹{result.get('EMA_50', '--')}"
    )

    e4.metric(
        "100",
        f"₹{result.get('EMA_100', '--')}"
    )

    e5.metric(
        "200",
        f"₹{result.get('EMA_200', '--')}"
    )

    st.caption(
        f"EMA Alignment: "
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

    st.caption("🔥 Supertrend")

    s1, s2 = st.columns(2)

    s1.metric(
        "Supertrend",
        f"₹{result.get('SUPERTREND', '--')}"
    )

    s2.metric(
        "ટ્રેન્ડ",
        result.get(
            "SUPERTREND_STATUS",
            "--"
        )
    )


    # =====================================================
    # VOLUME
    # =====================================================

    st.caption("📦 વોલ્યુમ અને બ્રેકઆઉટ")

    v1, v2, v3 = st.columns(3)

    v1.metric(
        "Volume",
        result.get(
            "VOLUME",
            "--"
        )
    )

    v2.metric(
        "Ratio",
        f"{result.get('VOLUME_RATIO', '--')}x"
    )

    v3.metric(
        "Breakout",
        result.get(
            "VOLUME_BREAKOUT",
            "--"
        )
    )


    # =====================================================
    # PRICE ACTION + 52W
    # =====================================================

    st.caption("🕯️ Price Action")

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

    h1, h2 = st.columns(2)

    h1.metric(
        "52W High",
        f"₹{result.get('52W_HIGH', '--')}"
    )

    h2.metric(
        "52W Low",
        f"₹{result.get('52W_LOW', '--')}"
    )


    # =====================================================
    # RISK
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '🛡️ જોખમ વ્યવસ્થાપન'
        '</div>',
        unsafe_allow_html=True
    )

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Risk Score",
        f"{risk_score_num:.0f}/100"
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
        f"{result.get('RISK_%', '--')}%"
    )

    r4, r5 = st.columns(2)

    r4.metric(
        "ATR 14",
        f"₹{result.get('ATR_14', '--')}"
    )

    r5.metric(
        "Stop Loss",
        f"₹{result.get('STOP_LOSS', '--')}"
    )


    # =====================================================
    # TECHNICAL SIGNAL
    # =====================================================

    final_signal = result.get(
        "FINAL_SIGNAL",
        "WAIT"
    )

    if final_signal == "BUY":

        st.success(
            "🟢 ટેક્નિકલ સિગ્નલ — ખરીદી"
        )

    elif final_signal == "HOLD":

        st.info(
            "🟡 ટેક્નિકલ સિગ્નલ — જાળવો"
        )

    elif final_signal == "REDUCE":

        st.warning(
            "🟠 ટેક્નિકલ સિગ્નલ — ઘટાડો"
        )

    elif final_signal == "EXIT":

        st.error(
            "🔴 ટેક્નિકલ સિગ્નલ — બહાર નીકળો"
        )

    else:

        st.warning(
            "🟡 ટેક્નિકલ સિગ્નલ — રાહ જુઓ"
        )


    st.caption(
        f"Data Date: "
        f"{result.get('DATA_DATE', '--')} | "
        f"Status: "
        f"{result.get('STATUS', '--')}"
    )


    # =====================================================
    # FUNDAMENTAL
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '🏢 ફન્ડામેન્ટલ વિશ્લેષણ'
        '</div>',
        unsafe_allow_html=True
    )


    if (
        fundamental.get(
            "FUNDAMENTAL_STATUS"
        )
        == "FRESH"
    ):

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


        # =================================================
        # VALUATION
        # =================================================

        st.caption("💰 Valuation")

        q1, q2 = st.columns(2)

        q1.metric(
            "PE",
            fundamental.get(
                "PE",
                "--"
            )
        )

        q2.metric(
            "Forward PE",
            fundamental.get(
                "FORWARD_PE",
                "--"
            )
        )


        # =================================================
        # FUNDAMENTAL SCORE
        # =================================================

        fs1, fs2, fs3 = st.columns(3)

        fs1.metric(
            "Fundamental",
            f"{fundamental_score_num:.0f}/100"
        )

        fs2.metric(
            "Zone",
            fundamental.get(
                "FUNDAMENTAL_ZONE",
                "--"
            )
        )

        fs3.metric(
            "Data Quality",
            f"{fundamental.get('DATA_QUALITY_%', '--')}%"
        )


        # =================================================
        # SCORE BREAKDOWN
        # =================================================

        st.caption(
            "📊 Fundamental Score Breakdown"
        )

        b1, b2, b3 = st.columns(3)

        b1.metric(
            "Growth",
            f"{fundamental.get('GROWTH_SCORE', '--')}/40"
        )

        b2.metric(
            "Quality",
            f"{fundamental.get('QUALITY_SCORE', '--')}/40"
        )

        b3.metric(
            "Valuation",
            f"{fundamental.get('VALUATION_SCORE', '--')}/20"
        )


        st.caption(
            f"Data Quality: "
            f"{fundamental.get('DATA_QUALITY', '--')}"
        )


    else:

        st.warning(
            "ફન્ડામેન્ટલ ડેટા ઉપલબ્ધ નથી."
        )

        if fundamental.get("ERROR"):

            st.caption(
                fundamental.get("ERROR")
            )


    # =====================================================
    # CLOSE STOCK CARD
    # =====================================================

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()


# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

st.header("📊 પોર્ટફોલિયો સારાંશ")

c1, c2, c3 = st.columns(3)

c1.metric(
    "પોર્ટફોલિયો કિંમત",
    "₹ —"
)

c2.metric(
    "પોર્ટફોલિયો રિટર્ન",
    "—"
)

c3.metric(
    "પોર્ટફોલિયો હેલ્થ",
    "— / 100"
)


# =========================================================
# CIO ACTION
# =========================================================

st.divider()

st.header("🎯 મુખ્ય રોકાણ નિર્ણય")

st.info(
    "NSE + Technical + Risk + Fundamental "
    "engines connected છે. "
    "PMS Master Score અને મુખ્ય રોકાણ નિર્ણય "
    "સક્રિય છે."
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🏦 RCS MASTER PMS | "
    "NSE Portfolio Decision System"
)
