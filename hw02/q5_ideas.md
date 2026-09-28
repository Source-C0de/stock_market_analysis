# Q5 — Ideas for Improving IPO Profitability

The basic strategy described in Q2/Q3 — buy an IPO on its first day and hold — is
unprofitable on average (medians are <1 for almost every holding window).  To make
it profitable, I'd combine fundamental, technical, sentiment and structural filters.

## 1. Filter by quality / fundamentals before buying
- **Profitability & cash flow**: buy only profitable IPOs with positive operating
  cash flow. Most speculative IPOs have none.
- **Underwriter reputation**: bulge-bracket lead (Goldman, Morgan Stanley, JPMorgan)
  usually means more institutional support, less "pump & dump" risk.
- **SCOOP rating**: iposcoop already scores IPOs; restrict to the highest tier.
- **Lock-up expiration awareness**: avoid stocks within ~30 days of lock-up expiry —
  supply overhang from insiders regularly produces drawdowns.

## 2. Time the entry (don't buy day 1)
- The data shows median price drops over 1–6 months. **Wait for a pull-back**:
  buy after a -20% / -30% drawdown from the first-day close, or after RSI crosses
  back above 30.
- Combine with a **moving-average filter** (Close > 50-day MA) to confirm the
  down-trend has ended.

## 3. Exit / holding-period optimisation with stops
- **Trailing stop-loss** of e.g. -10 % or **ATR-based stop** to cut losers quickly.
- **Take-profit** at +20 % / +50 % instead of blindly holding — captures the fat tail
  without giving back gains (most IPO pop-and-fade patterns).
- Use **position sizing** (Kelly / fixed-fractional) rather than equal weight.

## 4. Add complementary signals
- **Composite technical score**: combine RSI < 30, MACD bullish cross, price above
  200-day MA, and Bollinger-band reversion — the Q4 RSI strategy shows a +1.26 %
  edge with 55 % win rate, which compounds quickly with many trades.
- **Macro filter**: skip signals during high-rate / recession regimes (use
  FEDFUNDS, CPI, GDP growth already in the parquet).  Earnings risk is highest
  when liquidity is tightening.
- **Sector / ticker-type filter**: some sectors outperform post-IPO (software,
  healthcare biotech with catalysts); avoid "blank-check" SPACs and small
  financials.

## 5. Use sentiment / external data
- **First-day pop vs. offering price**: large first-day pops (>40 %) often mean
  the IPO was under-priced and there is still short-term downside — avoid; small
  pops or post-IPO drift setups have better follow-through.
- **Short interest**, **Google Trends**, **news sentiment**, **analyst coverage
  initiation** all have predictive value.

## 6. Machine-learning ranking model
- Train a classifier (logistic / GBDT) on historical IPOs to predict P(30-day
  return > 0) using SCOOP rating, fundamentals, underwriter, sector, market
  regime, first-day return, etc.  Only take the top-decile predictions.
- Use **walk-forward validation** to avoid look-ahead bias.

## 7. Risk controls that prevent the median-loss problem
- **No equal-weight long-only**: pair-trade the IPO against its sector ETF or
  short a weak peer (market-neutral IPO alpha is well documented).
- **Skip the IPO entirely** if the SPY/VIX regime is unfavourable — many "IPO
  alpha" studies disappear after conditioning on market state.
- **Cap gross exposure per IPO** and **max open positions** to limit tail risk.

### Concrete recipe I would test first
> 1. Universe: 2025 IPOs profitable at offering, lead-managed by a bulge-bracket
>    bank, SCOOP rating ≥ 4.
> 2. Entry: wait until the stock has traded ≥ 30 days, then buy on the next day
>    when Close < 80-day SMA **and** RSI < 35.
> 3. Exit: trailing 2×ATR stop, hard stop at -15 %, take-profit at +30 %.
> 4. Size: 1 % of equity per signal, max 10 concurrent positions.

This combines a **quality filter**, a **mean-reversion entry** (consistent with
the Q4 RSI evidence that oversold bounces work), and **disciplined exits**, which
together should flip the basic strategy's negative median into a positive
risk-adjusted return.
