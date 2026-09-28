"""Q4: RSI Strategy - Net Income."""
from __future__ import annotations

import os

import gdown
import pandas as pd

from helpers import find_col

FILE_ID = "1grCTCzMZKY5sJRtdbLVCXg8JXA8VPyg-"
OUT_FILE = "data.parquet"
SIGNAL_START = pd.Timestamp("2000-01-01")
SIGNAL_END = pd.Timestamp("2025-06-01")
INVESTMENT_PER_SIGNAL = 1000


def main() -> None:
    if not os.path.exists(OUT_FILE):
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        gdown.download(url, OUT_FILE, quiet=False)

    df = pd.read_parquet(OUT_FILE, engine="pyarrow")
    print(f"Shape: {df.shape}")

    date_col = find_col(df, "date", "datetime", "timestamp")
    if date_col is None:
        df = df.reset_index()
        date_col = df.columns[0]

    rsi_col = find_col(df, "rsi")
    growth_col = find_col(df, "growth_future_30d")
    print(f"Date col: {date_col}, RSI: {rsi_col}, growth_future_30d: {growth_col}")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    sig = df[
        (df[date_col] >= SIGNAL_START)
        & (df[date_col] <= SIGNAL_END)
        & (df[rsi_col] < 30)
    ].copy()
    print(f"Signals between {SIGNAL_START.date()} and {SIGNAL_END.date()}: {len(sig)}")

    excess = sig[growth_col] - 1
    net_income = INVESTMENT_PER_SIGNAL * excess.sum()
    avg_return = excess.mean()
    win_rate = (excess > 0).mean()

    print(f"\nNet income ($): {net_income:,.2f}")
    print(f"Net income ($ thousands): {net_income / 1000:,.2f}")
    print(f"Average 30-day return: {avg_return * 100:.2f}%")
    print(f"Win rate: {win_rate * 100:.2f}%")


if __name__ == "__main__":
    main()
