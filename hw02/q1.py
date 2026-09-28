"""Q1: IPO Withdrawn by Company Type."""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from helpers import fetch_table, find_col, to_currency_float

URL = "https://www.iposcoop.com/ipos-recently-filed/"

# (substring pattern -> Company Type label). Order matters: first match wins.
CLASSIFICATION_RULES: list[tuple[str, str]] = [
    ("Technologies", "Technologies"),
    ("Acquisition Corp", "Acquisition Corp"),
    ("Acquisition Corporation", "Acquisition Corp"),
    ("Corp", "Acquisition Corp"),
    ("Inc", "Inc."),
    ("Incorporated", "Inc."),
    ("Group", "Group"),
    ("Ltd", "Limited"),
    ("Limited", "Limited"),
    ("Holdings", "Holdings"),
    ("Holding", "Holdings"),
]


def _clean_name(name) -> str:
    """Strip parenthetical suffixes like '(Withdrawn)' from a company name."""
    if not isinstance(name, str):
        return ""
    return re.sub(r"\s*\(.*?\)\s*", "", name).strip()


def classify_company(name: str) -> str:
    """Classify a company by name based on the ordered rules in CLASSIFICATION_RULES."""
    name = _clean_name(name)
    for pattern, label in CLASSIFICATION_RULES:
        if pattern in name:
            return label
    return "Other"


def _avg_price(low: pd.Series, high: pd.Series) -> pd.Series:
    """Elementwise average of two price Series (NaN if either side is NaN)."""
    return (low + high) / 2.0


def main() -> None:
    df = fetch_table(URL)

    et_col = find_col(df, "expected to trade", "expected to trade date")
    name_col = find_col(df, "company", "company name", "issuer", "name")
    price_low_col = find_col(df, "price low")
    price_high_col = find_col(df, "price high")
    shares_col = next((c for c in df.columns if "shares" in c.lower()), None)
    vol_col = next((c for c in df.columns if "est" in c.lower() and "vol" in c.lower()), None)

    withdrawn = df[df[et_col].astype(str).str.strip().str.lower() == "withdrawn"].copy()
    print(f"Withdrawn rows: {len(withdrawn)}")

    withdrawn["Company Type"] = withdrawn[name_col].apply(classify_company)

    pl = to_currency_float(withdrawn[price_low_col])
    ph = to_currency_float(withdrawn[price_high_col])
    withdrawn["Avg_price"] = _avg_price(pl, ph)

    withdrawn["Shares (millions)"] = to_currency_float(withdrawn[shares_col])
    withdrawn["Est $ Vol (millions)"] = to_currency_float(withdrawn[vol_col])

    computed = withdrawn["Shares (millions)"] * withdrawn["Avg_price"]
    withdrawn["Shares_offered_value"] = np.where(
        computed.notna(),
        computed,
        withdrawn["Est $ Vol (millions)"],
    )

    summary = (
        withdrawn.groupby("Company Type")["Shares_offered_value"]
        .sum()
        .sort_values(ascending=False)
    )

    print("\nTotal withdrawn value (millions $) by Company Type:")
    print(summary)
    print("\nTop entry:")
    print(summary.head(1))


if __name__ == "__main__":
    main()
