import yfinance as yf
import pandas as pd


def safe_number(value):
    try:
        if value is None:
            return None

        value = float(value)

        if pd.isna(value):
            return None

        return value

    except Exception:
        return None


def growth_score(value):
    if value is None:
        return 0

    if value >= 20:
        return 20
    elif value >= 12:
        return 15
    elif value >= 5:
        return 10
    elif value >= 0:
        return 5

    return 0


def quality_score(roe, roce, debt):

    score = 0

    if roe is not None:

        if roe >= 20:
            score += 15
        elif roe >= 15:
            score += 12
        elif roe >= 10:
            score += 8
        elif roe >= 0:
            score += 4

    if roce is not None:

        if roce >= 20:
            score += 15
        elif roce >= 15:
            score += 12
        elif roce >= 10:
            score += 8
        elif roce >= 0:
            score += 4

    if debt is not None:

        if debt <= 0.5:
            score += 10
        elif debt <= 1:
            score += 7
        elif debt <= 2:
            score += 4

    return min(score, 40)


def fetch_fundamental_data(symbol):

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

        stock = yf.Ticker(ticker)

        info = stock.info

        if not info:

            return {
                "SYMBOL": symbol,
                "FUNDAMENTAL_STATUS": "NO_DATA"
            }

        revenue_growth = safe_number(
            info.get("revenueGrowth")
        )

        profit_growth = safe_number(
            info.get("earningsGrowth")
        )

        roe = safe_number(
            info.get("returnOnEquity")
        )

        roa = safe_number(
            info.get("returnOnAssets")
        )

        debt_to_equity = safe_number(
            info.get("debtToEquity")
        )

        pe = safe_number(
            info.get("trailingPE")
        )

        forward_pe = safe_number(
            info.get("forwardPE")
        )

        profit_margin = safe_number(
            info.get("profitMargins")
        )

        # Convert decimal growth values
        if revenue_growth is not None:
            revenue_growth *= 100

        if profit_growth is not None:
            profit_growth *= 100

        if roe is not None:
            roe *= 100

        if roa is not None:
            roa *= 100

        if profit_margin is not None:
            profit_margin *= 100

        # =========================
        # DATA QUALITY
        # =========================

        fields = [
            revenue_growth,
            profit_growth,
            roe,
            roa,
            debt_to_equity,
            pe
        ]

        available = sum(
            x is not None
            for x in fields
        )

        quality_pct = round(
            available /
            len(fields) *
            100
        )

        if quality_pct >= 80:
            data_quality = "HIGH"
        elif quality_pct >= 50:
            data_quality = "MEDIUM"
        else:
            data_quality = "LOW"

        # =========================
        # GROWTH SCORE
        # =========================

        revenue_score = growth_score(
            revenue_growth
        )

        profit_score = growth_score(
            profit_growth
        )

        growth_score_total = min(
            revenue_score +
            profit_score,
            40
        )

        # =========================
        # QUALITY SCORE
        # =========================

        quality = quality_score(
            roe,
            None,
            debt_to_equity
        )

        # =========================
        # VALUATION
        # =========================

        valuation_score = 0

        if pe is not None:

            if pe <= 15:
                valuation_score = 20
            elif pe <= 25:
                valuation_score = 15
            elif pe <= 40:
                valuation_score = 10
            elif pe <= 60:
                valuation_score = 5

        # =========================
        # FUNDAMENTAL SCORE
        # =========================

        fundamental_score = min(
            growth_score_total +
            quality +
            valuation_score,
            100
        )

        if data_quality == "LOW":

            fundamental_zone = "DATA LIMITED"

        elif fundamental_score >= 75:

            fundamental_zone = "STRONG"

        elif fundamental_score >= 60:

            fundamental_zone = "GOOD"

        elif fundamental_score >= 40:

            fundamental_zone = "AVERAGE"

        else:

            fundamental_zone = "WEAK"

        return {

            "SYMBOL": symbol,

            "REVENUE_GROWTH_%":
                None if revenue_growth is None
                else round(
                    revenue_growth,
                    2
                ),

            "PROFIT_GROWTH_%":
                None if profit_growth is None
                else round(
                    profit_growth,
                    2
                ),

            "ROE_%":
                None if roe is None
                else round(
                    roe,
                    2
                ),

            "ROA_%":
                None if roa is None
                else round(
                    roa,
                    2
                ),

            "DEBT_TO_EQUITY":
                None if debt_to_equity is None
                else round(
                    debt_to_equity,
                    2
                ),

            "PE":
                None if pe is None
                else round(
                    pe,
                    2
                ),

            "FORWARD_PE":
                None if forward_pe is None
                else round(
                    forward_pe,
                    2
                ),

            "PROFIT_MARGIN_%":
                None if profit_margin is None
                else round(
                    profit_margin,
                    2
                ),

            "DATA_QUALITY_%":
                quality_pct,

            "DATA_QUALITY":
                data_quality,

            "GROWTH_SCORE":
                growth_score_total,

            "QUALITY_SCORE":
                quality,

            "VALUATION_SCORE":
                valuation_score,

            "FUNDAMENTAL_SCORE":
                fundamental_score,

            "FUNDAMENTAL_ZONE":
                fundamental_zone,

            "FUNDAMENTAL_STATUS":
                "FRESH"
        }

    except Exception as error:

        return {

            "SYMBOL": symbol,

            "FUNDAMENTAL_STATUS":
                "DATA_ERROR",

            "ERROR":
                str(error)
        }


if __name__ == "__main__":

    result = fetch_fundamental_data(
        "CEMPRO"
    )

    print(
        "RCS MASTER PMS - "
        "FUNDAMENTAL ENGINE"
    )

    print(result)
