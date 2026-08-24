import pandas as pd
import yfinance as yf


def _safe_float(value):
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def _get_value(info, *keys):
    for key in keys:
        value = _safe_float(info.get(key))
        if value is not None:
            return value
    return None


def fetch_fundamental_data(symbol):

    symbol = str(symbol).strip().upper()

    result = {
        "SYMBOL": symbol,
        "FUNDAMENTAL_STATUS": "ERROR",

        "REVENUE_GROWTH_%": None,
        "PROFIT_GROWTH_%": None,
        "ROE_%": None,
        "ROA_%": None,
        "DEBT_TO_EQUITY": None,
        "PROFIT_MARGIN_%": None,

        "PE": None,
        "FORWARD_PE": None,

        "GROWTH_SCORE": 0,
        "QUALITY_SCORE": 0,
        "VALUATION_SCORE": 0,

        "FUNDAMENTAL_SCORE": 0,
        "FUNDAMENTAL_ZONE": "🔴 POOR",

        "DATA_QUALITY_%": 0,
        "DATA_QUALITY": "LOW",

        "ERROR": None
    }

    try:

        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info

        revenue_growth = _get_value(
            info,
            "revenueGrowth"
        )

        profit_growth = _get_value(
            info,
            "earningsGrowth"
        )

        roe = _get_value(
            info,
            "returnOnEquity"
        )

        roa = _get_value(
            info,
            "returnOnAssets"
        )

        debt_to_equity = _get_value(
            info,
            "debtToEquity"
        )

        profit_margin = _get_value(
            info,
            "profitMargins"
        )

        pe = _get_value(
            info,
            "trailingPE"
        )

        forward_pe = _get_value(
            info,
            "forwardPE"
        )

        # Convert ratios to percentage

        revenue_growth_pct = (
            revenue_growth * 100
            if revenue_growth is not None
            else None
        )

        profit_growth_pct = (
            profit_growth * 100
            if profit_growth is not None
            else None
        )

        roe_pct = (
            roe * 100
            if roe is not None
            else None
        )

        roa_pct = (
            roa * 100
            if roa is not None
            else None
        )

        profit_margin_pct = (
            profit_margin * 100
            if profit_margin is not None
            else None
        )

        # Growth Score / 40

        growth_score = 0

        if revenue_growth_pct is not None:

            if revenue_growth_pct >= 20:
                growth_score += 20

            elif revenue_growth_pct >= 10:
                growth_score += 15

            elif revenue_growth_pct >= 5:
                growth_score += 10

            elif revenue_growth_pct > 0:
                growth_score += 5

        if profit_growth_pct is not None:

            if profit_growth_pct >= 20:
                growth_score += 20

            elif profit_growth_pct >= 10:
                growth_score += 15

            elif profit_growth_pct >= 5:
                growth_score += 10

            elif profit_growth_pct > 0:
                growth_score += 5

        growth_score = min(growth_score, 40)

        # Quality Score / 40

        quality_score = 0

        if roe_pct is not None:

            if roe_pct >= 20:
                quality_score += 12

            elif roe_pct >= 15:
                quality_score += 10

            elif roe_pct >= 10:
                quality_score += 7

            elif roe_pct > 0:
                quality_score += 4

        if roa_pct is not None:

            if roa_pct >= 10:
                quality_score += 10

            elif roa_pct >= 7:
                quality_score += 8

            elif roa_pct >= 4:
                quality_score += 5

            elif roa_pct > 0:
                quality_score += 2

        if debt_to_equity is not None:

            if debt_to_equity <= 0.5:
                quality_score += 10

            elif debt_to_equity <= 1:
                quality_score += 8

            elif debt_to_equity <= 2:
                quality_score += 5

            elif debt_to_equity <= 3:
                quality_score += 2

        if profit_margin_pct is not None:

            if profit_margin_pct >= 20:
                quality_score += 8

            elif profit_margin_pct >= 10:
                quality_score += 6

            elif profit_margin_pct >= 5:
                quality_score += 4

            elif profit_margin_pct > 0:
                quality_score += 2

        quality_score = min(
            quality_score,
            40
        )

        # Valuation Score / 20

        valuation_score = 0

        selected_pe = None

        if (
            forward_pe is not None
            and forward_pe > 0
        ):
            selected_pe = forward_pe

        elif (
            pe is not None
            and pe > 0
        ):
            selected_pe = pe

        if selected_pe is not None:

            if selected_pe <= 15:
                valuation_score = 20

            elif selected_pe <= 20:
                valuation_score = 16

            elif selected_pe <= 25:
                valuation_score = 12

            elif selected_pe <= 35:
                valuation_score = 8

            elif selected_pe <= 50:
                valuation_score = 4

        fundamental_score = min(
            growth_score
            + quality_score
            + valuation_score,
            100
        )

        # Fundamental Zone

        if fundamental_score >= 80:
            fundamental_zone = "🟢 STRONG"

        elif fundamental_score >= 65:
            fundamental_zone = "🟢 GOOD"

        elif fundamental_score >= 50:
            fundamental_zone = "🟡 NEUTRAL"

        elif fundamental_score >= 35:
            fundamental_zone = "🟠 WEAK"

        else:
            fundamental_zone = "🔴 POOR"

        # Data Quality

        fields = [
            revenue_growth_pct,
            profit_growth_pct,
            roe_pct,
            roa_pct,
            debt_to_equity,
            profit_margin_pct,
            pe,
            forward_pe
        ]

        available = sum(
            value is not None
            for value in fields
        )

        data_quality_pct = round(
            available / len(fields) * 100,
            1
        )

        if data_quality_pct >= 80:
            data_quality = "HIGH"

        elif data_quality_pct >= 50:
            data_quality = "MEDIUM"

        else:
            data_quality = "LOW"

        result.update({

            "FUNDAMENTAL_STATUS": "FRESH",

            "REVENUE_GROWTH_%": (
                round(revenue_growth_pct, 2)
                if revenue_growth_pct is not None
                else None
            ),

            "PROFIT_GROWTH_%": (
                round(profit_growth_pct, 2)
                if profit_growth_pct is not None
                else None
            ),

            "ROE_%": (
                round(roe_pct, 2)
                if roe_pct is not None
                else None
            ),

            "ROA_%": (
                round(roa_pct, 2)
                if roa_pct is not None
                else None
            ),

            "DEBT_TO_EQUITY": (
                round(debt_to_equity, 2)
                if debt_to_equity is not None
                else None
            ),

            "PROFIT_MARGIN_%": (
                round(profit_margin_pct, 2)
                if profit_margin_pct is not None
                else None
            ),

            "PE": (
                round(pe, 2)
                if pe is not None
                else None
            ),

            "FORWARD_PE": (
                round(forward_pe, 2)
                if forward_pe is not None
                else None
            ),

            "GROWTH_SCORE": growth_score,
            "QUALITY_SCORE": quality_score,
            "VALUATION_SCORE": valuation_score,

            "FUNDAMENTAL_SCORE": fundamental_score,
            "FUNDAMENTAL_ZONE": fundamental_zone,

            "DATA_QUALITY_%": data_quality_pct,
            "DATA_QUALITY": data_quality
        })

        return result

    except Exception as error:

        result["ERROR"] = (
            f"{type(error).__name__}: {error}"
        )

        return result
