import pandas as pd
import yfinance as yf


def fetch_nse_data(symbol):
    symbol = symbol.strip().upper()

    ticker = symbol if symbol.endswith(".NS") else symbol + ".NS"

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
            data.columns = data.columns.get_level_values(0)

        data = data.dropna()

        close = float(data["Close"].iloc[-1])
        volume = int(data["Volume"].iloc[-1])

        previous_close = (
            float(data["Close"].iloc[-2])
            if len(data) > 1
            else close
        )

        change = close - previous_close

        change_pct = (
            change / previous_close * 100
            if previous_close != 0
            else 0
        )

        high_52w = float(data["Close"].max())
        low_52w = float(data["Close"].min())

        avg_volume_20 = float(
            data["Volume"].tail(20).mean()
        )

        volume_ratio = (
            volume / avg_volume_20
            if avg_volume_20 > 0
            else 0
        )

        return {
            "SYMBOL": symbol,
            "CMP": round(close, 2),
            "CHANGE": round(change, 2),
            "CHANGE_%": round(change_pct, 2),
            "VOLUME": volume,
            "AVG_VOLUME_20": round(avg_volume_20, 0),
            "VOLUME_RATIO": round(volume_ratio, 2),
            "52W_HIGH": round(high_52w, 2),
            "52W_LOW": round(low_52w, 2),
            "DATA_DATE": str(data.index[-1].date()),
            "STATUS": "FRESH"
        }

    except Exception as error:
        return {
            "SYMBOL": symbol,
            "STATUS": "DATA_ERROR",
            "ERROR": str(error)
        }


if __name__ == "__main__":
    result = fetch_nse_data("RELIANCE")
    print("RCS MASTER PMS - NSE DATA ENGINE")
    print(result)
