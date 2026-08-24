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

