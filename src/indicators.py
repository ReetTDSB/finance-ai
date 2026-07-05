"""
indicators.py
-------------
Calculates classic technical indicators from a price DataFrame.

Input:  a pandas DataFrame with at least a 'Close' column (as returned by yfinance).
Output: the same DataFrame with extra indicator columns added, plus a helper
        function `summarize_indicators` that condenses the latest values into a
        plain dict (used later to build prompts for the LLM).
"""

import numpy as np
import pandas as pd


def add_moving_average(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Adds a simple moving average column, e.g. MA_20."""
    df[f"MA_{window}"] = df["Close"].rolling(window=window).mean()
    return df


def add_volatility(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Adds rolling volatility = standard deviation of daily returns,
    annualized by sqrt(252) trading days.
    """
    daily_returns = df["Close"].pct_change()
    df["Volatility"] = daily_returns.rolling(window=window).std() * np.sqrt(252)
    return df


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Relative Strength Index (RSI).
    RSI > 70 is generally considered "overbought", RSI < 30 "oversold".
    """
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)  # avoid divide-by-zero
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    MACD (Moving Average Convergence Divergence).
    MACD line     = EMA_fast - EMA_slow
    Signal line   = EMA of MACD line
    Histogram     = MACD - Signal  (positive => bullish momentum, negative => bearish)
    """
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    return df


def add_sharpe_ratio(df: pd.DataFrame, risk_free_rate: float = 0.02) -> pd.DataFrame:
    """
    Optional: annualized Sharpe Ratio over the whole history window.
    Stored in df.attrs (not a per-row column) since Sharpe is a
    single summary statistic for the period.
    """
    daily_returns = df["Close"].pct_change().dropna()
    excess_returns = daily_returns - (risk_free_rate / 252)
    if daily_returns.std() == 0 or daily_returns.empty:
        sharpe = np.nan
    else:
        sharpe = (excess_returns.mean() / daily_returns.std()) * np.sqrt(252)
    df.attrs["sharpe_ratio"] = sharpe
    return df


def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function: runs every indicator in sequence."""
    df = df.copy()
    df = add_moving_average(df, 20)
    df = add_volatility(df, 20)
    df = add_rsi(df, 14)
    df = add_macd(df)
    df = add_sharpe_ratio(df)
    return df


def summarize_indicators(df: pd.DataFrame) -> dict:
    """
    Pulls the most recent indicator values into a simple dict.
    This dict is what gets turned into text for the LLM prompt.
    """
    latest = df.iloc[-1]

    def safe(val):
        return None if pd.isna(val) else round(float(val), 3)

    summary = {
        "last_close":   safe(latest["Close"]),
        "ma_20":        safe(latest.get("MA_20")),
        "volatility":   safe(latest.get("Volatility")),
        "rsi":          safe(latest.get("RSI")),
        "macd":         safe(latest.get("MACD")),
        "macd_signal":  safe(latest.get("MACD_Signal")),
        "macd_hist":    safe(latest.get("MACD_Hist")),
        "sharpe_ratio": safe(df.attrs.get("sharpe_ratio")),
    }

    # simple human-readable momentum tags
    if summary["macd_hist"] is not None:
        summary["macd_trend"] = "bullish" if summary["macd_hist"] > 0 else "bearish"
    else:
        summary["macd_trend"] = "unknown"

    if summary["rsi"] is not None:
        if summary["rsi"] > 70:
            summary["rsi_zone"] = "overbought"
        elif summary["rsi"] < 30:
            summary["rsi_zone"] = "oversold"
        else:
            summary["rsi_zone"] = "neutral"
    else:
        summary["rsi_zone"] = "unknown"

    return summary