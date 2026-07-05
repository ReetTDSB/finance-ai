"""
data_fetch.py
-------------
Thin wrapper around yfinance for pulling historical OHLCV data.
Keeping this isolated makes it easy to swap in another data
provider later (Alpha Vantage, Polygon, etc.) without touching
the rest of the app.
"""

import pandas as pd
import yfinance as yf


def fetch_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """
    Downloads historical price data for a single ticker.

    Args:
        ticker: stock symbol, e.g. "AAPL"
        period: how far back to look (e.g. "1mo", "6mo", "1y", "2y")
        interval: bar size (e.g. "1d", "1h")

    Returns:
        DataFrame indexed by date with columns: Open, High, Low, Close, Volume
    """
    data = yf.Ticker(ticker).history(period=period, interval=interval)

    if data.empty:
        raise ValueError(
            f"No data returned for ticker '{ticker}'. "
            "Check the symbol or your internet connection."
        )

    # Drop timezone info for simpler downstream handling
    data.index = data.index.tz_localize(None)
    return data


def fetch_company_info(ticker: str) -> dict:
    """
    Pulls basic company metadata (name, sector, market cap, etc).
    Wrapped in try/except because yfinance's .info can be flaky
    or incomplete for some tickers.
    """
    try:
        info = yf.Ticker(ticker).info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap"),
            "current_price": info.get("currentPrice"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
        }
    except Exception:
        return {"name": ticker, "sector": "Unknown", "industry": "Unknown"}