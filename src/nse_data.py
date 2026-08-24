import pandas as pd
import yfinance as yf


# =========================================================
# RSI
# =========================================================

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)

    return 100 - (100 / (1 + rs))


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
# SUPERTREND
# =========================================================

def calculate_supertrend(
    data,
    period=10,
    multiplier=3
):

    atr = calculate_atr(
        data,
        period
    )

    hl2 = (
        data["High"] +
        data["Low"]
    ) / 2

    upper = hl2 + (
        multiplier * atr
    )

    lower = hl2 - (
        multiplier * atr
    )

    direction = pd.Series(
        1,
        index=data.index,
        dtype=int
    )

    supertrend = pd.Series(
        index=data.index,
        dtype=float
    )

    for i in range(1, len(data)):

        if data["Close"].iloc[i] > upper.iloc[i - 1]:

            direction.iloc[i] = 1

        elif data["Close"].iloc[i] < lower.iloc[i - 1]:

            direction.iloc[i] = -1

        else:

            direction.iloc[i] = (
                direction.iloc[i - 1]
            )

        if direction.iloc[i] == 1:

            supertrend.iloc[i] = lower.iloc[i]

        else:

            supertrend.iloc[i] = upper.iloc[i]

    return supertrend, direction


# =========================================================
# CPR + PIVOT
# =========================================================

def calculate_cpr_pivot(data):

    high = float(data["High"].iloc[-2])
    low = float(data["Low"].iloc[-2])
    close = float(data["Close"].iloc[-2])

    pivot = (
        high +
        low +
        close
    ) / 3

    bc = (
        high +
        low
    ) / 2

    tc = (
        pivot +
        bc
    ) / 2

    r1 = (
        2 * pivot
    ) - low

    s1 = (
        2 * pivot
    ) - high

    r2 = pivot + (
        high - low
    )

    s2 = pivot - (
        high - low
    )

    r3 = high + (
        2 * (pivot - low)
    )

    s3 = low - (
        2 * (high - pivot)
    )

    return {
        "PIVOT": pivot,
        "CPR_BC": bc,
        "CPR_TC": tc,
        "R1": r1,
        "R2": r2,
        "R3": r3,
        "S1": s1,
        "S2": s2,
        "S3": s3
    }


# =========================================================
# SUPPORT / RESISTANCE
# =========================================================

def calculate_support_resistance(data):

    recent = data.tail(60)

    support = float(
        recent["Low"].min()
    )

    resistance = float(
        recent["High"].max()
    )

    return support, resistance


# =========================================================
# RESAMPLE D/W/M
# =========================================================

def resample_ohlcv(data, timeframe):

    rule_map = {
        "D": "1D",
        "W": "1W",
        "M": "1ME"
    }

    rule = rule_map.get(
        timeframe,
        "1D"
    )

    result = data.resample(rule).agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    })

    return result.dropna()


# =========================================================
# NSE DATA ENGINE
# =========================================================

def fetch_nse_data(symbol):

    symbol = str(
        symbol
    ).strip().upper()

    ticker_map = {
        "CEMPRO": "CEMPRO.NS",
        "SHRIRAMFIN": "SHRIRAMFIN.NS"
    }

    ticker = ticker_map.get(
        symbol,
        symbol if symbol.endswith(".NS")
        else symbol + ".NS"
    )

    try:

        data = yf.download(
            ticker,
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if data.empty:

            return {
                "SYMBOL": symbol,
                "STATUS": "NO_DATA"
            }

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

                return {
                    "SYMBOL": symbol,
                    "STATUS": "MISSING_COLUMNS"
                }

        data = data[
            required_columns
        ].dropna()

        if len(data) < 30:

            return {
                "SYMBOL": symbol,
                "STATUS": "INSUFFICIENT_DATA"
            }

        # =====================================================
        # PRICE
        # =====================================================

        cmp = float(
            data["Close"].iloc[-1]
        )

        previous_close = float(
            data["Close"].iloc[-2]
        )

        change = (
            cmp -
            previous_close
        )

        change_pct = (
            change /
            previous_close *
            100
            if previous_close != 0
            else 0
        )

        # =====================================================
        # EMA
        # =====================================================

        close = data["Close"]

        ema_10 = close.ewm(
            span=10,
            adjust=False
        ).mean()

        ema_20 = close.ewm(
            span=20,
            adjust=False
        ).mean()

        ema_50 = close.ewm(
            span=50,
            adjust=False
        ).mean()

        ema_100 = close.ewm(
            span=100,
            adjust=False
        ).mean()

        ema_200 = close.ewm(
            span=200,
            adjust=False
        ).mean()

        e10 = float(ema_10.iloc[-1])
        e20 = float(ema_20.iloc[-1])
        e50 = float(ema_50.iloc[-1])
        e100 = float(ema_100.iloc[-1])
        e200 = float(ema_200.iloc[-1])

        # =====================================================
        # RSI
        # =====================================================

        rsi_series = calculate_rsi(
            close,
            14
        )

        rsi_14 = float(
            rsi_series.iloc[-1]
        )

        # =====================================================
        # MACD
        # =====================================================

        ema_12 = close.ewm(
            span=12,
            adjust=False
        ).mean()

        ema_26 = close.ewm(
            span=26,
            adjust=False
        ).mean()

        macd_line = (
            ema_12 -
            ema_26
        )

        macd_signal = (
            macd_line
            .ewm(
                span=9,
                adjust=False
            )
            .mean()
        )

        macd_hist = (
            macd_line -
            macd_signal
        )

        macd_value = float(
            macd_line.iloc[-1]
        )

        macd_signal_value = float(
            macd_signal.iloc[-1]
        )

        macd_hist_value = float(
            macd_hist.iloc[-1]
        )

        # =====================================================
        # SUPERTREND
        # =====================================================

        supertrend, st_direction = (
            calculate_supertrend(
                data,
                10,
                3
            )
        )

        supertrend_value = float(
            supertrend.iloc[-1]
        )

        supertrend_status = (
            "BULLISH"
            if int(st_direction.iloc[-1]) == 1
            else "BEARISH"
        )

        # =====================================================
        # VOLUME
        # =====================================================

        volume = data["Volume"]

        current_volume = int(
            volume.iloc[-1]
        )

        avg_volume_20 = float(
            volume.tail(20).mean()
        )

        volume_ratio = (
            current_volume /
            avg_volume_20
            if avg_volume_20 > 0
            else 0
        )

        volume_breakout = (
            "YES"
            if volume_ratio >= 2
            else "NO"
        )

        # =====================================================
        # 52 WEEK
        # =====================================================

        one_year = data.tail(252)

        high_52w = float(
            one_year["Close"].max()
        )

        low_52w = float(
            one_year["Close"].min()
        )

        # =====================================================
        # PRICE ACTION
        # =====================================================

        today_open = float(
            data["Open"].iloc[-1]
        )

        today_high = float(
            data["High"].iloc[-1]
        )

        today_low = float(
            data["Low"].iloc[-1]
        )

        candle_body = (
            cmp -
            today_open
        )

        candle_range = (
            today_high -
            today_low
        )

        body_pct = (
            abs(candle_body) /
            candle_range *
            100
            if candle_range > 0
            else 0
        )

        if candle_body > 0:
            price_action = "BULLISH"

        elif candle_body < 0:
            price_action = "BEARISH"

        else:
            price_action = "NEUTRAL"

        # =====================================================
        # EMA ALIGNMENT
        # =====================================================

        if (
            cmp > e10
            and e10 > e20
            and e20 > e50
            and e50 > e100
            and e100 > e200
        ):

            ema_alignment = "BULLISH"

        elif (
            cmp < e10
            and e10 < e20
            and e20 < e50
            and e50 < e100
            and e100 < e200
        ):

            ema_alignment = "BEARISH"

        else:

            ema_alignment = "MIXED"

        # =====================================================
        # TECHNICAL SCORE
        # =====================================================

        technical_score = 0

        if ema_alignment == "BULLISH":
            technical_score += 25

        elif ema_alignment == "MIXED":
            technical_score += 12

        if 60 <= rsi_14 < 70:
            technical_score += 20

        elif 50 <= rsi_14 < 60:
            technical_score += 15

        elif rsi_14 >= 70:
            technical_score += 10

        elif 40 <= rsi_14 < 50:
            technical_score += 5

        if macd_hist_value > 0:
            technical_score += 20

        if int(
            st_direction.iloc[-1]
        ) == 1:

            technical_score += 20

        if volume_ratio >= 2:
            technical_score += 10

        elif volume_ratio >= 1:
            technical_score += 5

        # =====================================================
        # TECHNICAL ZONE
        # =====================================================

        if technical_score >= 80:
            technical_zone = "STRONG BULLISH"

        elif technical_score >= 65:
            technical_zone = "BULLISH"

        elif technical_score >= 50:
            technical_zone = "NEUTRAL"

        elif technical_score >= 35:
            technical_zone = "WEAK"

        else:
            technical_zone = "BEARISH"

        # =====================================================
        # ATR + RISK
        # =====================================================

        atr_series = calculate_atr(
            data,
            14
        )

        atr_value = float(
            atr_series.iloc[-1]
        )

        stop_loss = (
            cmp -
            (2 * atr_value)
        )

        risk_pct = (
            (
                cmp -
                stop_loss
            )
            / cmp *
            100
        )

        if risk_pct <= 5:
            risk_level = "LOW"

        elif risk_pct <= 10:
            risk_level = "MEDIUM"

        else:
            risk_level = "HIGH"

        risk_score = round(
            max(
                0,
                min(
                    100,
                    100 -
                    (risk_pct * 5)
                )
            )
        )

        # =====================================================
        # FINAL SIGNAL
        # =====================================================

        bullish_points = 0
        bearish_points = 0

        if ema_alignment == "BULLISH":
            bullish_points += 1

        elif ema_alignment == "BEARISH":
            bearish_points += 1

        if rsi_14 >= 50:
            bullish_points += 1
        else:
            bearish_points += 1

        if macd_hist_value > 0:
            bullish_points += 1
        else:
            bearish_points += 1

        if int(
            st_direction.iloc[-1]
        ) == 1:

            bullish_points += 1

        else:

            bearish_points += 1

        if volume_ratio >= 1:
            bullish_points += 1

        if bullish_points >= 4:
            final_signal = "BUY"

        elif bullish_points == 3:
            final_signal = "HOLD"

        elif bearish_points >= 4:
            final_signal = "REDUCE"

        else:
            final_signal = "WAIT"

        # =====================================================
        # CPR + PIVOT
        # =====================================================

        cpr = calculate_cpr_pivot(
            data
        )

        # =====================================================
        # SUPPORT / RESISTANCE
        # =====================================================

        support, resistance = (
            calculate_support_resistance(
                data
            )
        )

        # =====================================================
        # MOMENTUM TRIGGER
        # =====================================================

        recent_high = float(
            data["High"].tail(20).max()
        )

        momentum_trigger = recent_high

        if cmp >= momentum_trigger:

            momentum_status = "ACTIVE"

        else:

            momentum_status = "WAIT"

        # =====================================================
        # BUY + BUY ON DIP
        # =====================================================

        buy_level = max(
            e20,
            cpr["PIVOT"]
        )

        buy_on_dip_low = max(
            e50,
            cpr["S1"]
        )

        buy_on_dip_high = min(
            e20,
            cpr["PIVOT"]
        )

        # Safety correction
        if buy_on_dip_high < buy_on_dip_low:

            buy_on_dip_low = min(
                e20,
                e50
            )

            buy_on_dip_high = max(
                e20,
                e50
            )

        # =====================================================
        # TARGET ENGINE
        # =====================================================

        swing_target = max(
            resistance,
            cpr["R1"]
        )

        long_term_target = max(
            high_52w,
            resistance * 1.20
        )

        # =====================================================
        # STOCK ZONE
        # =====================================================

        if (
            technical_score >= 65
            and macd_hist_value >= 0
            and int(st_direction.iloc[-1]) == 1
        ):

            stock_zone = "BULL"

        elif (
            technical_score < 35
            and macd_hist_value < 0
            and int(st_direction.iloc[-1]) == -1
        ):

            stock_zone = "BEAR"

        else:

            stock_zone = "NEUTRAL"

        # =====================================================
        # CHART DATA
        # =====================================================

        chart_data = data.tail(300).copy()

        chart_data["EMA_10"] = (
            chart_data["Close"]
            .ewm(
                span=10,
                adjust=False
            )
            .mean()
        )

        chart_data["EMA_20"] = (
            chart_data["Close"]
            .ewm(
                span=20,
                adjust=False
            )
            .mean()
        )

        chart_data["EMA_50"] = (
            chart_data["Close"]
            .ewm(
                span=50,
                adjust=False
            )
            .mean()
        )

        chart_data["EMA_100"] = (
            chart_data["Close"]
            .ewm(
                span=100,
                adjust=False
            )
            .mean()
        )

        chart_data["EMA_200"] = (
            chart_data["Close"]
            .ewm(
                span=200,
                adjust=False
            )
            .mean()
        )

        chart_data["SUPERTREND"] = (
            supertrend.tail(
                len(chart_data)
            ).values
        )

        chart_data = (
            chart_data
            .reset_index()
        )

        chart_data["Date"] = (
            pd.to_datetime(
                chart_data[
                    chart_data.columns[0]
                ]
            )
            .dt.strftime("%Y-%m-%d")
        )

        chart_data = chart_data[
            [
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "EMA_10",
                "EMA_20",
                "EMA_50",
                "EMA_100",
                "EMA_200",
                "SUPERTREND"
            ]
        ]

        # =====================================================
        # D / W / M DATA
        # =====================================================

        daily_data = resample_ohlcv(
            data,
            "D"
        )

        weekly_data = resample_ohlcv(
            data,
            "W"
        )

        monthly_data = resample_ohlcv(
            data,
            "M"
        )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        return {

            "SYMBOL": symbol,

            "CMP": round(
                cmp,
                2
            ),

            "CHANGE": round(
                change,
                2
            ),

            "CHANGE_%": round(
                change_pct,
                2
            ),

            "EMA_10": round(e10, 2),
            "EMA_20": round(e20, 2),
            "EMA_50": round(e50, 2),
            "EMA_100": round(e100, 2),
            "EMA_200": round(e200, 2),

            "EMA_ALIGNMENT":
                ema_alignment,

            "RSI_14": round(
                rsi_14,
                2
            ),

            "MACD": round(
                macd_value,
                2
            ),

            "MACD_SIGNAL": round(
                macd_signal_value,
                2
            ),

            "MACD_HIST": round(
                macd_hist_value,
                2
            ),

            "SUPERTREND": round(
                supertrend_value,
                2
            ),

            "SUPERTREND_STATUS":
                supertrend_status,

            "VOLUME":
                current_volume,

            "AVG_VOLUME_20":
                round(
                    avg_volume_20,
                    0
                ),

            "VOLUME_RATIO":
                round(
                    volume_ratio,
                    2
                ),

            "VOLUME_BREAKOUT":
                volume_breakout,

            "PRICE_ACTION":
                price_action,

            "BODY_%":
                round(
                    body_pct,
                    2
                ),

            "52W_HIGH":
                round(
                    high_52w,
                    2
                ),

            "52W_LOW":
                round(
                    low_52w,
                    2
                ),

            "ATR_14":
                round(
                    atr_value,
                    2
                ),

            "STOP_LOSS":
                round(
                    stop_loss,
                    2
                ),

            "RISK_%":
                round(
                    risk_pct,
                    2
                ),

            "RISK_SCORE":
                risk_score,

            "RISK_LEVEL":
                risk_level,

            "TECHNICAL_SCORE":
                technical_score,

            "TECHNICAL_ZONE":
                technical_zone,

            "FINAL_SIGNAL":
                final_signal,

            # =================================================
            # NEW CHART / TRADE FIELDS
            # =================================================

            "PIVOT": round(
                cpr["PIVOT"],
                2
            ),

            "CPR_BC": round(
                cpr["CPR_BC"],
                2
            ),

            "CPR_TC": round(
                cpr["CPR_TC"],
                2
            ),

            "R1": round(
                cpr["R1"],
                2
            ),

            "R2": round(
                cpr["R2"],
                2
            ),

            "R3": round(
                cpr["R3"],
                2
            ),

            "S1": round(
                cpr["S1"],
                2
            ),

            "S2": round(
                cpr["S2"],
                2
            ),

            "S3": round(
                cpr["S3"],
                2
            ),

            "SUPPORT": round(
                support,
                2
            ),

            "RESISTANCE": round(
                resistance,
                2
            ),

            "BUY_LEVEL": round(
                buy_level,
                2
            ),

            "BUY_ON_DIP_LOW": round(
                buy_on_dip_low,
                2
            ),

            "BUY_ON_DIP_HIGH": round(
                buy_on_dip_high,
                2
            ),

            "MOMENTUM_TRIGGER": round(
                momentum_trigger,
                2
            ),

            "MOMENTUM_STATUS":
                momentum_status,

            "SWING_TARGET": round(
                swing_target,
                2
            ),

            "LONG_TERM_TARGET":
                round(
                    long_term_target,
                    2
                ),

            "STOCK_ZONE":
                stock_zone,

            # =================================================
            # CHART DATA
            # =================================================

            "CHART_DATA":
                chart_data,

            "DAILY_DATA":
                daily_data,

            "WEEKLY_DATA":
                weekly_data,

            "MONTHLY_DATA":
                monthly_data,

            "DATA_DATE":
                str(
                    data.index[-1].date()
                ),

            "STATUS":
                "FRESH"
        }

    except Exception as error:

        return {

            "SYMBOL": symbol,

            "STATUS":
                "DATA_ERROR",

            "ERROR":
                f"{type(error).__name__}: {error}"
        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    result = fetch_nse_data(
        "CEMPRO"
    )

    print(
        "R.S MASTER STOCK GUIDE"
    )

    print(
        result
    )
