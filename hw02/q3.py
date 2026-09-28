"""Q3: Optimal holding period (1-12 months) for 2025 IPOs."""
from __future__ import annotations

import numpy as np
import pandas as pd

from helpers import (
    clean_tickers,
    download_close_long,
    fetch_table,
    parse_percent,
    TRADING_DAYS_PER_MONTH,
)

IPOSCOOP_2025_URL = "https://www.iposcoop.com/2025-pricings/"
CUTOFF_DATE = pd.Timestamp("2025-09-01")
CACHE_PATH = "cache/yf_2025_ipos.parquet"


def main() -> None:
    df = fetch_table(IPOSCOOP_2025_URL)
    df["Offer Date"] = pd.to_datetime(df["Offer Date"], errors="coerce")
    df["Return_pct"] = parse_percent(df["Return"])

    filt = df[(df["Offer Date"] < CUTOFF_DATE) & (df["Return_pct"] != 0)].copy()
    print(f"After filter: {len(filt)}")

    tickers = clean_tickers(filt["Symbol"])
    close_long = download_close_long(tickers, period="2y", cache_path=CACHE_PATH)
    print(f"close_long shape: {close_long.shape}")

    growth_cols: list[str] = []
    for m in range(1, 13):
        col = f"future_growth_{m}_m"
        days = TRADING_DAYS_PER_MONTH * m
        close_long[col] = close_long.groupby("Ticker")["Close"].shift(-days) / close_long["Close"]
        growth_cols.append(col)

    close_long["min_date"] = close_long.groupby("Ticker")["Date"].transform("min")
    on_min = close_long[close_long["Date"] == close_long["min_date"]]
    print(f"on_min shape: {on_min.shape}")

    print("\nDescribe on min-date (entry point) records:")
    print(on_min[growth_cols].describe())

    medians = on_min[growth_cols].median()
    means = on_min[growth_cols].mean()
    print("\nMedians:")
    print(medians)
    print("\nMeans:")
    print(means)

    best_col = medians.idxmax()
    best_val = medians.max()
    print(f"\nBest holding period: {best_col}, median growth: {best_val:.4f}")


if __name__ == "__main__":
    main()
