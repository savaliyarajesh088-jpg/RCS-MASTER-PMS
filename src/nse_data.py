import pandas as pd
import yfinance as yf


def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)

    rsi = 100 - (100 / (1 + rs))

    return rsi


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

        if isinstance(data.columns, pd.MultiIndex):

            data.columns = (
                data.columns
                .get_level_values(0)
            )

        data = data.dropna()

        close = data["Close"]

        volume = data["Volume"]

        # =========================
        # PRICE DATA
        # =========================

        cmp = float(close.iloc[-1])

        previous_close = (
            float(close.iloc[-2])
            if len(close) > 1
            else cmp
        )

        change = cmp - previous_close

        change_pct = (
            change / previous_close * 100
            if previous_close != 0
            else 0
        )

        # =========================
        # EMA
        # =========================

        ema_10 = close.ewm(
            span=10,
            adjust=False
        ).mean().iloc[-1]

        ema_20 = close.ewm(
            span=20,
            adjust=False
        ).mean().iloc[-1]

        ema_50 = close.ewm(
            span=50,
            adjust=False
        ).mean().iloc[-1]

        ema_100 = close.ewm(
            span=100,
            adjust=False
        ).mean().iloc[-1]

        ema_200 = close.ewm(
            span=200,
            adjust=False
        ).mean().iloc[-1]

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

        macd_line = ema_12 - ema_26

        macd_signal = macd_line.ewm(
            span=9,
            adjust=False
        ).mean()

        macd_hist = (
            macd_line - macd_signal
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
            current_volume / avg_volume_20
            if avg_volume_20 > 0
            else 0
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
        # EMA ALIGNMENT
        # =========================

        ema_alignment = "MIXED"

        if (
            cmp > ema_10
            and ema_10 > ema_20
            and ema_20 > ema_50
            and ema_50 > ema_100
            and ema_100 > ema_200
        ):

            ema_alignment = "BULLISH"

        elif (
            cmp < ema_10
            and ema_10 < ema_20
            and ema_20 < ema_50
            and ema_50 < ema_100
            and ema_100 < ema_200
        ):

            ema_alignment = "BEARISH"

        # =========================
        # TECHNICAL SCORE
        # =========================

        technical_score = 0

        if ema_alignment == "BULLISH":
            technical_score += 25

        elif ema_alignment == "MIXED":
            technical_score += 12

        if 50 <= rsi_14 < 70:
            technical_score += 15

        elif 60 <= rsi_14 < 70:
            technical_score += 20

        elif rsi_14 >= 70:
            technical_score += 10

        elif 40 <= rsi_14 < 50:
            technical_score += 5

        if macd_hist.iloc[-1] > 0:
            technical_score += 20

        if volume_ratio >= 2:
            technical_score += 10

        elif volume_ratio >= 1:
            technical_score += 5

        # =========================
        # TECHNICAL ZONE
        # =========================

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

        # =========================
        # FINAL RESULT
        # =========================

        return {

            "SYMBOL": symbol,

            "CMP": round(cmp, 2),

            "CHANGE": round(
                change,
                2
            ),

            "CHANGE_%": round(
                change_pct,
                2
            ),

            "EMA_10": round(
                float(ema_10),
                2
            ),

            "EMA_20": round(
                float(ema_20),
                2
            ),

            "EMA_50": round(
                float(ema_50),
                2
            ),

            "EMA_100": round(
                float(ema_100),
                2
            ),

            "EMA_200": round(
                float(ema_200),
                2
            ),

            "RSI_14": round(
                rsi_14,
                2
            ),

            "MACD": round(
                float(macd_line.iloc[-1]),
                2
            ),

            "MACD_SIGNAL": round(
                float(macd_signal.iloc[-1]),
                2
            ),

            "MACD_HIST": round(
                float(macd_hist.iloc[-1]),
                2
            ),

            "EMA_ALIGNMENT":
                ema_alignment,

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

            "TECHNICAL_SCORE":
                technical_score,

            "TECHNICAL_ZONE":
                technical_zone,

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
        "RELIANCE"
    )

    print(
        "RCS MASTER PMS - "
        "TECHNICAL ENGINE"
    )

    print(result)
