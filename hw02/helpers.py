"""Shared helpers for hw02 scripts."""
from __future__ import annotations

import io
import os
from typing import Iterable

import numpy as np
import pandas as pd
import requests
import yfinance as yf

USER_AGENT = "Mozilla/5.0"
TRADING_DAYS_PER_MONTH = 21


# ---------------------------------------------------------------------------
# HTTP / scraping
# ---------------------------------------------------------------------------
def fetch_table(url: str, **kwargs) -> pd.DataFrame:
    """Fetch a single HTML table from a URL via pandas.read_html."""
    headers = kwargs.pop("headers", {"User-Agent": USER_AGENT})
    timeout = kwargs.pop("timeout", 30)
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    tables = pd.read_html(io.StringIO(resp.text), **kwargs)
    if not tables:
        raise ValueError(f"No tables found at {url}")
    return tables[0]


def clean_tickers(symbols: Iterable) -> list[str]:
    """Normalise an iterable of ticker symbols into a sorted unique list."""
    return sorted({str(t).strip() for t in symbols if t and str(t).lower() != "nan"})


def parse_percent(series: pd.Series) -> pd.Series:
    """Vectorised '12.34%' -> 0.1234 conversion (NaN-safe)."""
    s = series.astype(str).str.rstrip("%").str.strip()
    return pd.to_numeric(s, errors="coerce") / 100.0


def to_currency_float(series: pd.Series) -> pd.Series:
    """Vectorised '$1,234.56' -> 1234.56 (NaN-safe)."""
    s = series.astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.strip()
    return pd.to_numeric(s, errors="coerce")


# ---------------------------------------------------------------------------
# Column discovery
# ---------------------------------------------------------------------------
def find_col(df: pd.DataFrame, *candidates: str, contains: tuple[str, ...] = ()) -> str | None:
    """Find a column by exact lower-case match or by 'contains' substrings."""
    lowers = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lowers:
            return lowers[cand.lower()]
    for c in df.columns:
        cl = c.lower()
        if all(sub in cl for sub in contains):
            return c
    return None


# ---------------------------------------------------------------------------
# Yfinance download
# ---------------------------------------------------------------------------
def download_close_long(
    tickers: list[str],
    period: str = "2y",
    cache_path: str | None = None,
) -> pd.DataFrame:
    """Download OHLCV for ``tickers`` and return a long (Date, Ticker, Close) frame.

    If ``cache_path`` is given and the parquet file exists, it is loaded instead
    of re-hitting Yahoo.
    """
    if cache_path and os.path.exists(cache_path):
        raw = pd.read_parquet(cache_path, engine="pyarrow")
        cached_tickers = raw.columns.get_level_values(0).unique().tolist()
        missing = [t for t in tickers if t not in cached_tickers]
        if not missing:
            keep = clean_tickers(tickers)
            return _raw_to_close_long(raw, keep)

    raw = yf.download(
        tickers=tickers,
        period=period,
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    if cache_path:
        os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
        raw.to_parquet(cache_path, engine="pyarrow")

    keep = [t for t in tickers if t in raw.columns.get_level_values(0) and raw[t].notna().any().any()]
    return _raw_to_close_long(raw, keep)


def _raw_to_close_long(raw: pd.DataFrame, keep: list[str]) -> pd.DataFrame:
    """Convert the wide (Ticker, Field) DataFrame into a long (Date, Ticker, Close) frame."""
    parts = []
    for t in keep:
        sub = raw[t]
        sub.columns = pd.MultiIndex.from_product([[t], sub.columns])
        parts.append(sub)
    long = pd.concat(parts, axis=1)
    close = long.xs("Close", axis=1, level=1)
    close_long = (
        close.stack(future_stack=True)
        .rename("Close")
        .reset_index()
    )
    close_long.columns = ["Date", "Ticker", "Close"]
    return close_long.dropna(subset=["Close"]).sort_values(["Ticker", "Date"]).reset_index(drop=True)
