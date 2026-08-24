import pandas as pd
import numpy as np
import yfinance as yf


# =========================================================
# SAFE HELPERS
# =========================================================

def _safe_float(value, default=None):
    try:
        if value is None:
            return default

        if pd.isna(value):
            return default

        return float(value)

    except Exception:
        return default


# =========================================================
# RSI
# =========================================================

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

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

    atr = calculate_atr(data, period)

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

        if pd.isna(upper.iloc[i - 1]):
            direction.iloc[i] = direction.iloc[i - 1]

        elif data["Close"].iloc[i] > upper.iloc[i - 1]:

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

    previous_high = data["High"].shift(1)
    previous_low = data["Low"].shift(1)
    previous_close = data["Close"].shift(1)

    pivot = (
        previous_high +
        previous_low +
        previous_close
    ) / 3

    bc = (
        previous_high +
        previous_low
    ) / 2

    tc = (
        pivot * 2
    ) - bc

    r1 = (
        2 * pivot
    ) - previous_low

    s1 = (
        2 * pivot
    ) - previous_high

    r2 = (
        pivot +
        (
            previous_high -
            previous_low
        )
    )

    s2 = (
        pivot -
        (
            previous_high -
            previous_low
        )
    )

    return (
        pivot,
        tc,
        bc,
        r1,
        s1,
        r2,
        s2
    )


# =========================================================
# SUPPORT / RESISTANCE
# =========================================================

def calculate_support_resistance(
    data,
    lookback=20
):

    recent = data.tail(lookback)

    support = _safe_float(
        recent["Low"].min()
    )

    resistance = _safe_float(
        recent["High"].max()
    )

    return support, resistance


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

        # =====================================================
        # DOWNLOAD DAILY DATA
        # =====================================================

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
                    "STATUS": "MISSING_COLUMN",
                    "ERROR": column
                }

        data = data[
            required_columns
        ].dropna()

        if len(data) < 60:

            return {
                "SYMBOL": symbol,
                "STATUS": "INSUFFICIENT_DATA"
            }

        # =====================================================
        # PRICE
        # =====================================================

        close = data["Close"]
        volume = data["Volume"]

        cmp = _safe_float(
            close.iloc[-1],
            0
        )

        previous_close = _safe_float(
            close.iloc[-2],
            0
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

        e10 = _safe_float(
            ema_10.iloc[-1],
            0
        )

        e20 = _safe_float(
            ema_20.iloc[-1],
            0
        )

        e50 = _safe_float(
            ema_50.iloc[-1],
            0
        )

        e100 = _safe_float(
            ema_100.iloc[-1],
            0
        )

        e200 = _safe_float(
            ema_200.iloc[-1],
            0
        )

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
        # RSI
        # =====================================================

        rsi_series = calculate_rsi(
            close,
            14
        )

        rsi_14 = _safe_float(
            rsi_series.iloc[-1],
            50
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

        macd_value = _safe_float(
            macd_line.iloc[-1],
            0
        )

        macd_signal_value = _safe_float(
            macd_signal.iloc[-1],
            0
        )

        macd_hist_value = _safe_float(
            macd_hist.iloc[-1],
            0
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

        supertrend_value = _safe_float(
            supertrend.iloc[-1],
            cmp
        )

        supertrend_status = (
            "BULLISH"
            if int(
                st_direction.iloc[-1]
            ) == 1
            else "BEARISH"
        )

        # =====================================================
        # ATR
        # =====================================================

        atr_series = calculate_atr(
            data,
            14
        )

        atr_value = _safe_float(
            atr_series.iloc[-1],
            0
        )

        # =====================================================
        # VOLUME
        # =====================================================

        current_volume = _safe_float(
            volume.iloc[-1],
            0
        )

        avg_volume_20 = _safe_float(
            volume.tail(20).mean(),
            0
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

        year_data = data.tail(252)

        high_52w = _safe_float(
            year_data["High"].max(),
            cmp
        )

        low_52w = _safe_float(
            year_data["Low"].min(),
            cmp
        )

        distance_from_52w_high = (
            (
                high_52w -
                cmp
            )
            /
            high_52w *
            100
            if high_52w
            else 0
        )

        distance_from_52w_low = (
            (
                cmp -
                low_52w
            )
            /
            low_52w *
            100
            if low_52w
            else 0
        )

        # =====================================================
        # PRICE ACTION
        # =====================================================

        today_open = _safe_float(
            data["Open"].iloc[-1],
            cmp
        )

        today_high = _safe_float(
            data["High"].iloc[-1],
            cmp
        )

        today_low = _safe_float(
            data["Low"].iloc[-1],
            cmp
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
        # CPR + PIVOT
        # =====================================================

        (
            pivot_series,
            tc_series,
            bc_series,
            r1_series,
            s1_series,
            r2_series,
            s2_series
        ) = calculate_cpr_pivot(data)

        pivot = _safe_float(
            pivot_series.iloc[-1],
            cmp
        )

        cpr_tc = _safe_float(
            tc_series.iloc[-1],
            cmp
        )

        cpr_bc = _safe_float(
            bc_series.iloc[-1],
            cmp
        )

        r1 = _safe_float(
            r1_series.iloc[-1],
            cmp
        )

        s1 = _safe_float(
            s1_series.iloc[-1],
            cmp
        )

        r2 = _safe_float(
            r2_series.iloc[-1],
            cmp
        )

        s2 = _safe_float(
            s2_series.iloc[-1],
            cmp
        )

        if cmp > cpr_tc:

            cpr_status = "ABOVE CPR"

        elif cmp < cpr_bc:

            cpr_status = "BELOW CPR"

        else:

            cpr_status = "INSIDE CPR"

        # =====================================================
        # SUPPORT / RESISTANCE
        # =====================================================

        support_20, resistance_20 = (
            calculate_support_resistance(
                data,
                20
            )
        )

        support_50, resistance_50 = (
            calculate_support_resistance(
                data,
                50
            )
        )

        # Nearest meaningful support

        support_candidates = [
            s1,
            s2,
            support_20,
            support_50,
            e20,
            e50,
            supertrend_value
        ]

        valid_supports = [
            x for x in support_candidates
            if x is not None
            and x < cmp
        ]

        support = (
            max(valid_supports)
            if valid_supports
            else min(support_candidates)
        )

        # Nearest meaningful resistance

        resistance_candidates = [
            r1,
            r2,
            resistance_20,
            resistance_50,
            high_52w
        ]

        valid_resistances = [
            x for x in resistance_candidates
            if x is not None
            and x > cmp
        ]

        resistance = (
            min(valid_resistances)
            if valid_resistances
            else max(resistance_candidates)
        )

        # =====================================================
        # MOMENTUM LEVEL
        # =====================================================

        momentum_level = max(
            e10,
            e20,
            resistance
        )

        momentum_buffer = (
            momentum_level * 0.01
        )

        momentum_trigger = (
            momentum_level +
            momentum_buffer
        )

        if cmp >= momentum_trigger:

            momentum_status = "ACTIVE"

        elif cmp >= momentum_level * 0.99:

            momentum_status = "NEAR"

        else:

            momentum_status = "WAITING"

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

        technical_score = min(
            technical_score,
            100
        )

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
        # COMMON STOP LOSS
        # =====================================================

        atr_stop = (
            cmp -
            (2 * atr_value)
        )

        technical_support_stop = (
            support -
            (0.5 * atr_value)
        )

        stop_loss = max(
            atr_stop,
            technical_support_stop
        )

        if stop_loss >= cmp:

            stop_loss = atr_stop

        risk_pct = (
            (
                cmp -
                stop_loss
            )
            /
            cmp *
            100
            if cmp > 0
            else 0
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
                    risk_pct * 5
                )
            )
        )

        # =====================================================
        # SWING TARGET
        # =====================================================

        swing_target_1 = max(
            resistance,
            cmp + (1.5 * atr_value)
        )

        swing_target_2 = max(
            swing_target_1 + atr_value,
            cmp + (3 * atr_value)
        )

        # =====================================================
        # LONG TERM TARGET
        # =====================================================

        long_target_1 = max(
            high_52w,
            cmp + (4 * atr_value)
        )

        long_target_2 = max(
            long_target_1 + (2 * atr_value),
            cmp + (8 * atr_value)
        )

        # =====================================================
        # RISK / REWARD
        # =====================================================

        swing_reward = (
            swing_target_1 -
            cmp
        )

        risk_amount = (
            cmp -
            stop_loss
        )

        swing_rr = (
            swing_reward /
            risk_amount
            if risk_amount > 0
            else 0
        )

        # =====================================================
        # SIGNAL ENGINE
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

        if cmp > pivot:

            bullish_points += 1

        else:

            bearish_points += 1

        # =====================================================
        # FINAL SIGNAL
        # =====================================================

        if (
            technical_score >= 80
            and bullish_points >= 5
            and volume_ratio >= 1
        ):

            final_signal = "STRONG BUY"

        elif (
            bullish_points >= 5
            and technical_score >= 65
        ):

            final_signal = "BUY"

        elif (
            technical_score >= 50
            and cmp > support
            and risk_level != "HIGH"
        ):

            final_signal = "BUY ON DIP"

        elif bullish_points >= 3:

            final_signal = "HOLD"

        elif bearish_points >= 4:

            final_signal = "REDUCE"

        else:

            final_signal = "WAIT"

        # =====================================================
        # ZONE ENGINE
        # =====================================================

        if technical_score >= 70:

            market_zone = "🐂 BULL"

        elif technical_score <= 35:

            market_zone = "🐻 BEAR"

        else:

            market_zone = "🐷 PIG"

        # =====================================================
        # BUY / SELL LEVELS
        # =====================================================

        buy_level = max(
            support,
            min(
                e20,
                cmp
            )
        )

        dip_buy_level = (
            support +
            (0.25 * atr_value)
        )

        sell_level = resistance

        # =====================================================
        # DATA QUALITY
        # =====================================================

        data_quality = 100

        if len(data) < 200:

            data_quality -= 10

        if pd.isna(
            rsi_series.iloc[-1]
        ):

            data_quality -= 15

        if pd.isna(
            atr_series.iloc[-1]
        ):

            data_quality -= 15

        data_quality = max(
            0,
            data_quality
        )

        # =====================================================
        # CHART DATA
        # =====================================================

        chart_data = data.copy()

        chart_data["EMA_10"] = ema_10
        chart_data["EMA_20"] = ema_20
        chart_data["EMA_50"] = ema_50
        chart_data["EMA_100"] = ema_100
        chart_data["EMA_200"] = ema_200

        chart_data["SUPERTREND"] = supertrend

        chart_data["RSI_14"] = rsi_series

        chart_data["MACD"] = macd_line
        chart_data["MACD_SIGNAL"] = macd_signal
        chart_data["MACD_HIST"] = macd_hist

        chart_data["VOLUME_AVG_20"] = (
            volume.rolling(20).mean()
        )

        chart_data["PIVOT"] = pivot_series
        chart_data["CPR_TC"] = tc_series
        chart_data["CPR_BC"] = bc_series
        chart_data["R1"] = r1_series
        chart_data["S1"] = s1_series
        chart_data["R2"] = r2_series
        chart_data["S2"] = s2_series

        # Keep chart manageable

        chart_data = chart_data.tail(
            500
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

            # EMA

            "EMA_10": round(e10, 2),
            "EMA_20": round(e20, 2),
            "EMA_50": round(e50, 2),
            "EMA_100": round(e100, 2),
            "EMA_200": round(e200, 2),

            "EMA_ALIGNMENT":
                ema_alignment,

            # Momentum

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

            # Supertrend

            "SUPERTREND": round(
                supertrend_value,
                2
            ),

            "SUPERTREND_STATUS":
                supertrend_status,

            # Volume

            "VOLUME": int(
                current_volume
            ),

            "AVG_VOLUME_20": round(
                avg_volume_20,
                0
            ),

            "VOLUME_RATIO": round(
                volume_ratio,
                2
            ),

            "VOLUME_BREAKOUT":
                volume_breakout,

            # Price action

            "PRICE_ACTION":
                price_action,

            "BODY_%": round(
                body_pct,
                2
            ),

            # 52W

            "52W_HIGH": round(
                high_52w,
                2
            ),

            "52W_LOW": round(
                low_52w,
                2
            ),

            "DISTANCE_FROM_52W_HIGH_%":
                round(
                    distance_from_52w_high,
                    2
                ),

            "DISTANCE_FROM_52W_LOW_%":
                round(
                    distance_from_52w_low,
                    2
                ),

            # ATR / Risk

            "ATR_14": round(
                atr_value,
                2
            ),

            "STOP_LOSS": round(
                stop_loss,
                2
            ),

            "RISK_%": round(
                risk_pct,
                2
            ),

            "RISK_SCORE":
                risk_score,

            "RISK_LEVEL":
                risk_level,

            # CPR

            "PIVOT": round(
                pivot,
                2
            ),

            "CPR_TC": round(
                cpr_tc,
                2
            ),

            "CPR_BC": round(
                cpr_bc,
                2
            ),

            "CPR_STATUS":
                cpr_status,

            "R1": round(r1, 2),
            "R2": round(r2, 2),
            "S1": round(s1, 2),
            "S2": round(s2, 2),

            # Support Resistance

            "SUPPORT": round(
                support,
                2
            ),

            "RESISTANCE": round(
                resistance,
                2
            ),

            "SUPPORT_20": round(
                support_20,
                2
            ),

            "RESISTANCE_20": round(
                resistance_20,
                2
            ),

            "SUPPORT_50": round(
                support_50,
                2
            ),

            "RESISTANCE_50": round(
                resistance_50,
                2
            ),

            # Momentum

            "MOMENTUM_LEVEL": round(
                momentum_level,
                2
            ),

            "MOMENTUM_TRIGGER": round(
                momentum_trigger,
                2
            ),

            "MOMENTUM_STATUS":
                momentum_status,

            # Buy Sell

            "BUY_LEVEL": round(
                buy_level,
                2
            ),

            "DIP_BUY_LEVEL": round(
                dip_buy_level,
                2
            ),

            "SELL_LEVEL": round(
                sell_level,
                2
            ),

            # Targets

            "SWING_TARGET_1": round(
                swing_target_1,
                2
            ),

            "SWING_TARGET_2": round(
                swing_target_2,
                2
            ),

            "LONG_TARGET_1": round(
                long_target_1,
                2
            ),

            "LONG_TARGET_2": round(
                long_target_2,
                2
            ),

            "SWING_RR": round(
                swing_rr,
                2
            ),

            # Score

            "TECHNICAL_SCORE":
                technical_score,

            "TECHNICAL_ZONE":
                technical_zone,

            "MARKET_ZONE":
                market_zone,

            "FINAL_SIGNAL":
                final_signal,

            "BULLISH_POINTS":
                bullish_points,

            "BEARISH_POINTS":
                bearish_points,

            # Quality

            "DATA_QUALITY_%":
                data_quality,

            # Dates

            "DATA_DATE":
                str(
                    data.index[-1].date()
                ),

            "STATUS":
                "FRESH",

            # Chart

            "CHART_DATA":
                chart_data

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
# OPTIONAL DIRECT TEST
# =========================================================

if __name__ == "__main__":

    result = fetch_nse_data(
        "CEMPRO"
    )

    print(
        "\n=========================================="
    )

    print(
        "R.S MASTER STOCK GUIDE"
    )

    print(
        "NSE DATA ENGINE TEST"
    )

    print(
        "=========================================="
    )

    for key, value in result.items():

        if key != "CHART_DATA":

            print(
                f"{key}: {value}"
            )
