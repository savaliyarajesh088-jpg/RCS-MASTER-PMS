
    return supertrend, direction


# =========================
# NSE DATA ENGINE
# =========================

def fetch_nse_data(symbol):

    symbol = symbol.strip().upper()

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
            period="1y",
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

        data = data.dropna()

        if len(data) < 30:

            return {
                "SYMBOL": symbol,
                "STATUS": "INSUFFICIENT_DATA"
            }

        close = data["Close"]
        volume = data["Volume"]

        # =========================
        # PRICE
        # =========================

        cmp = float(
            close.iloc[-1]
        )

        previous_close = float(
            close.iloc[-2]
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

        # =========================
        # EMA
        # =========================

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

        # =========================
        # RSI
        # =========================

        rsi_series = calculate_rsi(
            close,
            14
        )

        rsi_14 = float(
            rsi_series.iloc[-1]
        )

        # =========================
        # MACD
        # =========================

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

        # =========================
        # SUPERTREND
        # =========================

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

        # =========================
        # VOLUME
        # =========================

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

        # =========================
        # 52 WEEK
        # =========================

        high_52w = float(
            close.max()
        )

        low_52w = float(
            close.min()
        )

        # =========================
        # PRICE ACTION
        # =========================

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

        # =========================
        # EMA ALIGNMENT
        # =========================

        e10 = float(
            ema_10.iloc[-1]
        )

        e20 = float(
            ema_20.iloc[-1]
        )

        e50 = float(
            ema_50.iloc[-1]
        )

        e100 = float(
            ema_100.iloc[-1]
        )

        e200 = float(
            ema_200.iloc[-1]
        )

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

        # =========================
        # TECHNICAL SCORE
        # =========================

        technical_score = 0

        if ema_alignment == "BULLISH":

            technical_score += 25

        elif ema_alignment == "MIXED":

            technical_score += 12

        # Correct RSI ordering
        if 60 <= rsi_14 < 70:

            technical_score += 20

        elif 50 <= rsi_14 < 60:

            technical_score += 15

        elif rsi_14 >= 70:

            technical_score += 10

        elif 40 <= rsi_14 < 50:

            technical_score += 5

        if float(
            macd_hist.iloc[-1]
        ) > 0:

            technical_score += 20

        if int(
            st_direction.iloc[-1]
        ) == 1:

            technical_score += 20

        if volume_ratio >= 2:

            technical_score += 10

        elif volume_ratio >= 1:

            technical_score += 5

        # =========================
        # TECHNICAL ZONE
        # =========================

        if technical_score >= 80:

            technical_zone = (
                "STRONG BULLISH"
            )

        elif technical_score >= 65:

            technical_zone = "BULLISH"

        elif technical_score >= 50:

            technical_zone = "NEUTRAL"

        elif technical_score >= 35:

            technical_zone = "WEAK"

        else:

            technical_zone = "BEARISH"

        # =========================
        # RISK ENGINE
        # =========================

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

        # =========================
        # FINAL SIGNAL
        # =========================

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

        if float(
            macd_hist.iloc[-1]
        ) > 0:

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

        # =========================
        # FINAL RESULT
        # =========================

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

            "EMA_10": round(
                e10,
                2
            ),

            "EMA_20": round(
                e20,
                2
            ),

            "EMA_50": round(
                e50,
                2
            ),

            "EMA_100": round(
                e100,
                2
            ),

            "EMA_200": round(
                e200,
                2
            ),

            "EMA_ALIGNMENT":
                ema_alignment,

            "RSI_14": round(
                rsi_14,
                2
            ),

            "MACD": round(
                float(
                    macd_line.iloc[-1]
                ),
                2
            ),

            "MACD_SIGNAL": round(
                float(
                    macd_signal.iloc[-1]
                ),
                2
            ),

            "MACD_HIST": round(
                float(
                    macd_hist.iloc[-1]
                ),
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
                str(error)
        }


if __name__ == "__main__":

    result = fetch_nse_data(
        "CEMPRO"
    )

    print(
        "RCS MASTER PMS - "
        "TECHNICAL + RISK ENGINE"
    )

    print(result)
