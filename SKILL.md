---
name: cycle-of-price-action
description: Analyze stocks and ETFs with the Cycle of Price Action (CPA) framework popularized by Oliver Kell. Use for CPA stage classification, Reversal Extension, Wedge Pop, EMA Crossback, Base & Break, Exhaustion Extension, Wedge Drop, CPA trade plans, setup grading, or multi-ticker CPA screens. Do not use for generic fundamental analysis that does not request CPA.
---

# Cycle of Price Action Stock Analysis

Produce disciplined, data-grounded CPA analysis for stocks and ETFs. Determine the cycle stage before discussing action, cite the evidence, define invalidation from price structure, and state uncertainty.

This skill is inspired by the public Oliver Kell / Cycle of Price Action framework. Its numerical thresholds and grading rubric are implementation heuristics for consistent analysis; do not attribute them to Oliver Kell as official rules.

## Non-negotiable rules

- Obtain actual market data before making a current-stage claim.
- Treat price structure as primary; use volume, moving averages, relative strength, and catalysts as confirmation.
- Distinguish a completed daily bar from an incomplete intraday bar.
- Never fabricate a quote, indicator, volume figure, catalyst, pivot, stop, or target.
- Never call benchmark-relative strength "strong" without calculating it against a benchmark.
- Accept `NO CLEAN CPA SETUP` when stages conflict or risk is poorly defined.
- Do not silently install packages, use credentials, sign up for services, spend money, or place trades.
- Return analysis in the user's language.

## Resolve the request

Identify the ticker, exchange when ambiguous, requested timeframe, whether current/live data is required, and whether the user wants analysis only or a trade plan. Default to a daily chart for classification and weekly data for context. Do not ask a question when the ticker can be resolved confidently.

Default benchmark:

- Growth, technology, and high-beta equities: `QQQ`.
- Broad-market equities: `SPY`.
- Use a sector ETF when it is clearly more informative, and explain the choice.

## Obtain and validate data

Prefer sources in this order:

1. A host market-data or finance tool.
2. A reputable web/chart source.
3. A configured brokerage or financial API.
4. User-provided or local OHLCV files.
5. The bundled standard-library fetcher as a convenience fallback.

For ordinary daily analysis, obtain the latest quote, at least 6 months of daily OHLCV (preferably 12 months), and matching benchmark history. Inspect 1.5-3 years of weekly data when major levels or cycle maturity matter.

Validate the newest date, missing sessions, suspicious zero volume, splits, ticker changes, and whether the newest candle is complete. If current data is unavailable, analyze only through the last verified bar and state its date.

The fetcher requires Python 3.10+ and no third-party packages:

```bash
python scripts/fetch_market_data.py NVDA QQQ --start 2025-01-01 --output-dir <temporary-directory>
```

It uses Yahoo Finance's public chart endpoint as a best-effort fallback. Treat its quote metadata as potentially delayed, cross-check important current values, and never weaken the stale-data or incomplete-candle safeguards because the script returned successfully.

## Calculate deterministic evidence

When normalized CSV data is available, use the bundled calculator instead of reimplementing indicators:

```bash
python scripts/calculate_cpa.py \
  --symbol NVDA --symbol-csv <temporary-directory>/NVDA_daily.csv \
  --benchmark QQQ --benchmark-csv <temporary-directory>/QQQ_daily.csv
```

During the market session, pass `--exclude-last-bar` when the CSV's final daily row is still forming. Use `--as-of YYYY-MM-DD` for historical analysis. Read the JSON output and inspect its `data_quality.warnings`; script output is evidence, not an automatic stage verdict.

The calculator produces:

- EMA10, EMA20, SMA50, and SMA200;
- Wilder ATR(14), VOL20, relative volume, Ext10, and Ext20;
- 20-day and 63-day returns and benchmark-relative performance;
- rolling highs/lows, recent gaps, recent daily bars, and weekly context;
- data-quality warnings and provenance fields.

If the script cannot run, calculate the same definitions directly and disclose that path. Do not confuse benchmark-relative strength with RSI.

## Classify the CPA stage

Before assigning a stage, read [references/cpa-stages.md](references/cpa-stages.md). Evaluate all six stages rather than matching the first familiar pattern:

1. Reversal Extension
2. Wedge Pop
3. EMA Crossback
4. Base & Break
5. Exhaustion Extension
6. Wedge Drop

Use this evidence order:

1. Price structure and cycle location.
2. Broader trend and overhead supply.
3. EMA10/EMA20 behavior.
4. Volume.
5. Relative strength.
6. SMA50/SMA200 context.
7. Catalyst context.

Return one primary stage, an optional secondary/developing stage, and `High`, `Medium`, or `Low` confidence. A chart may be transitional; never force a classification.

## Define action and risk

For a full report, setup grade, entry/stop discussion, intraday request, or multi-ticker screen, read [references/reporting-and-risk.md](references/reporting-and-risk.md).

When a setup exists, identify an observable trigger, preferred entry area, structural invalidation, stop reference, risk per share and percent, nearby resistance, and realistic reward in R. Do not move a stop merely to manufacture attractive R/R. Do not invent a fixed target when a trailing EMA or structural exit is more appropriate.

Use exactly one action state:

- `BUYABLE NOW`
- `WATCH / WAIT FOR TRIGGER`
- `HOLD / TREND INTACT`
- `TRIM / EXTENDED`
- `DEFENSIVE / EXIT RISK`
- `NO CLEAN CPA SETUP`

Use `BUYABLE NOW` only when current verified data shows that the trigger occurred and price is not materially extended.

## Current-session handling

If the user asks for "today", "current", or "now":

- Resolve the actual current date and U.S. market session.
- Use the latest completed daily bar for stable indicator context.
- Present intraday or extended-hours price separately as provisional evidence.
- Do not confirm a daily breakout before the close unless the user explicitly requests intraday execution analysis.
- State the as-of time, timezone, session, newest data date, and whether the latest bar is complete.

## Final verification

Before answering, verify that:

- actual market data and sources are identified;
- indicator values trace to the stated OHLCV series;
- EMA10/20, SMA50/200 when history allows, ATR, volume, and benchmark RS were checked;
- the selected stage is supported by structure rather than one threshold;
- invalidation comes from an observable chart level;
- incomplete or stale data is labeled;
- confidence is reduced when evidence conflicts;
- the response ends with: `This is a rules-based chart analysis, not personalized financial advice.`
