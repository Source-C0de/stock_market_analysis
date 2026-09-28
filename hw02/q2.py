"""Q2: Median Sharpe Ratio for 2025 IPOs (as of 11 Sep 2026)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from helpers import (
    clean_tickers,
    download_close_long,
    fetch_table,
    parse_percent,
)

IPOSCOOP_2025_URL = "https://www.iposcoop.com/2025-pricings/"
TARGET_DATE = pd.Timestamp("2026-09-11")
CUTOFF_DATE = pd.Timestamp("2025-09-01")
RISK_FREE_RATE = 0.05
CACHE_PATH = "cache/yf_2025_ipos.parquet"


def main() -> None:
    df = fetch_table(IPOSCOOP_2025_URL)
    df["Offer Date"] = pd.to_datetime(df["Offer Date"], errors="coerce")
    df["Return_pct"] = parse_percent(df["Return"])

    filt = df[(df["Offer Date"] < CUTOFF_DATE) & (df["Return_pct"] != 0)].copy()
    print(f"After filter (before {CUTOFF_DATE.date()}, return != 0): {len(filt)}")

    tickers = clean_tickers(filt["Symbol"])
    print(f"Unique tickers: {len(tickers)}")

    close_long = download_close_long(tickers, period="2y", cache_path=CACHE_PATH)
    print(f"close_long shape: {close_long.shape}")

    g = close_long.groupby("Ticker")["Close"]
    close_long["growth_252d"] = g.shift(0) / g.shift(252)
    close_long["volatility"] = g.rolling(30).std().reset_index(level=0, drop=True) * np.sqrt(252)
    close_long["Sharpe"] = (close_long["growth_252d"] - RISK_FREE_RATE) / close_long["volatility"]

    available_dates = close_long["Date"].unique()
    if TARGET_DATE in available_dates:
        day = close_long[close_long["Date"] == TARGET_DATE]
    else:
        prior = [d for d in available_dates if d <= TARGET_DATE]
        if not prior:
            raise SystemExit("No data available at or before target date")
        chosen = max(prior)
        print(f"Target {TARGET_DATE.date()} not found; using {pd.Timestamp(chosen).date()}")
        day = close_long[close_long["Date"] == chosen]

    print(f"Day used: {day['Date'].iloc[0]}")
    print(f"Number of stocks: {day['Ticker'].nunique()}")
    print(f"Count growth_252d: {day['growth_252d'].notna().sum()}")
    print(f"Count Sharpe: {day['Sharpe'].notna().sum()}")

    cols = ["growth_252d", "volatility", "Sharpe"]
    print("\nDescribe():")
    print(day[cols].describe())

    finite_sharpe = day["Sharpe"].replace([np.inf, -np.inf], np.nan)
    print(f"\nMedian Sharpe (inf excluded): {finite_sharpe.median():.4f}")
    print(f"Median growth_252d: {day['growth_252d'].median():.4f}")
    print(f"Mean growth_252d: {day['growth_252d'].mean():.4f}")


if __name__ == "__main__":
    main()
