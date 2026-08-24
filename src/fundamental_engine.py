
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


    # =====================================================
    # EMA
    # =====================================================

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


    # =====================================================
    # MOMENTUM
    # =====================================================

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


    # =====================================================
    # SUPERTREND
    # =====================================================

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


    # =====================================================
    # VOLUME
    # =====================================================

    st.write(
        "### 📦 Volume & Breakout"
    )

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


    # =====================================================
    # PRICE ACTION
    # =====================================================

    st.write(
        "### 🕯️ Price Action"
    )

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


    # =====================================================
    # 52 WEEK
    # =====================================================

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
    # TECHNICAL SCORE
    # =====================================================

    st.write(
        "### 🎯 Technical Status"
    )

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


    # =====================================================
    # RISK
    # =====================================================

    st.write(
        "### 🛡️ Risk Management"
    )

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


    # =====================================================
    # FINAL TECHNICAL SIGNAL
    # =====================================================

    st.write(
        "### 🚦 Technical Final Signal"
    )

    final_signal = result.get(
        "FINAL_SIGNAL",
        "WAIT"
    )

    if final_signal == "BUY":

        st.success(
            "🟢 BUY"
        )

    elif final_signal == "HOLD":

        st.info(
            "🟡 HOLD"
        )

    elif final_signal == "REDUCE":

        st.warning(
            "🟠 REDUCE"
        )

    elif final_signal == "EXIT":

        st.error(
            "🔴 EXIT"
        )

    else:

        st.warning(
            "🟡 WAIT"
        )


    # =====================================================
    # DATA STATUS
    # =====================================================

    st.caption(
        f"Data Date: "
        f"{result.get('DATA_DATE', '--')} | "
        f"Status: "
        f"{result.get('STATUS', '--')}"
    )


    # =====================================================
    # FUNDAMENTAL ENGINE
    # =====================================================

    st.write(
        "### 🏢 Fundamental Analysis"
    )

    fundamental = fetch_fundamental_data(
        symbol
    )


    if (
        fundamental.get(
            "FUNDAMENTAL_STATUS"
        )
        == "FRESH"
    ):

        # -------------------------------------------------
        # GROWTH
        # -------------------------------------------------

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


        # -------------------------------------------------
        # QUALITY
        # -------------------------------------------------

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


        # -------------------------------------------------
        # VALUATION
        # -------------------------------------------------

        st.write(
            "### 💰 Valuation"
        )

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


        # -------------------------------------------------
        # FUNDAMENTAL SCORE
        # -------------------------------------------------

        st.write(
            "### 🎯 Fundamental Score"
        )

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


        # -------------------------------------------------
        # SCORE BREAKDOWN
        # -------------------------------------------------

        st.write(
            "### 📊 Fundamental Score Breakdown"
        )

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

        if fundamental.get(
            "ERROR"
        ):

            st.caption(
                fundamental.get(
                    "ERROR"
                )
            )


    st.divider()


# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

st.header(
    "📊 Portfolio Summary"
)

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

st.header(
    "🎯 CIO Action"
)

st.info(
    "NSE + Technical + Risk + Fundamental "
    "engines are connected. PMS Score and "
    "CIO Decision Engine will be added next."
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.write(
    "RCS MASTER PMS | NSE Portfolio Decision System"
)
