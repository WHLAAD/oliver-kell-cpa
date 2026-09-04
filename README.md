# Cycle of Price Action Stock Analysis

**English** | [简体中文](README.zh-CN.md)

A portable Codex Skill for analyzing stocks and ETFs with the Cycle of Price Action (CPA) framework.

This is an independent, unofficial implementation. Its numerical thresholds and setup grade are consistency heuristics, not rules attributed to Oliver Kell.

## Strategy background

Cycle of Price Action is a discretionary swing-trading and trend-analysis framework popularized by 2020 U.S. Investing Champion Oliver Kell. It organizes a stock's behavior into a recurring sequence:

`Reversal Extension → Wedge Pop → EMA Crossback → Base & Break → Exhaustion Extension → Wedge Drop`

The framework combines price and volume, the 10- and 20-period exponential moving averages, higher-timeframe context, relative strength, entries near defined support, and exits when a trend becomes extended or loses structure. Kell describes his broader approach as an adaptation of CAN SLIM, informed by William O'Neil, Jesse Livermore, Nicolas Darvas, and Richard Wyckoff. See the [official CPA overview](https://kelltrading.com/) and the [publisher record for *Victory in Stock Trading*](https://books.google.com/books/about/Victory_in_Stock_Trading_Strategies_and.html?id=QhctEAAAQBAJ).

## Historical performance and annualized return

The [official December 2020 standings](https://financial-competitions.com/previousstandings/2021/1/13/december-2020-standings) reported a **+941.1% return** for Oliver Kell in the 2020 U.S. Investing Championship stock division through December 31, 2020. The competition tracks designated real-money accounts under its published [rules](https://financial-competitions.com/rules).

That figure is a single competition-year result—not a multi-year compound annual growth rate, a backtest of every CPA signal, or an expected return for users of this Skill. This repository has no independently verified long-term track record, so it does **not** claim that CPA can reliably produce a particular annualized return. A defensible expectation would require fully specified trading rules, position sizing, transaction costs, slippage, survivorship-bias controls, out-of-sample testing, and drawdown analysis. The 2020 result was exceptional and should not be used as a planning assumption; past performance does not guarantee future results.

## What it provides

- Natural-language and explicit `$cycle-of-price-action` invocation.
- Six-stage CPA classification guidance.
- Deterministic EMA, SMA, Wilder ATR, volume, extension, and benchmark-relative-strength calculations.
- A no-dependency market-data fallback for daily Yahoo Finance chart data.
- Full-report, trade-plan, intraday, and multi-ticker output conventions.
- Standard-library unit tests for the calculator.

## Repository layout

```text
cycle-of-price-action/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── calculate_cpa.py
│   └── fetch_market_data.py
├── references/
│   ├── cpa-stages.md
│   └── reporting-and-risk.md
├── tests/test_calculate_cpa.py
├── README.md
└── README.zh-CN.md
```

## Install

Ask Codex to install the Skill from this repository:

```text
Use $skill-installer to install the Skill from
https://github.com/WHLAAD/cycle-of-price-action
```

Restart Codex if the newly installed Skill does not appear immediately.

## Use

Natural language:

```text
Analyze NVDA today using the CPA framework.
```

Explicit invocation:

```text
Use $cycle-of-price-action to rank NVDA, MU, and AVGO by CPA setup quality.
```

## Deterministic calculation workflow

The scripts require Python 3.10+ and use only the standard library.

```bash
python scripts/fetch_market_data.py NVDA QQQ --start 2025-01-01 --output-dir .tmp/cpa-data
python scripts/calculate_cpa.py \
  --symbol NVDA --symbol-csv .tmp/cpa-data/NVDA_daily.csv \
  --benchmark QQQ --benchmark-csv .tmp/cpa-data/QQQ_daily.csv \
  --output .tmp/cpa-data/NVDA_cpa.json
```

The fetcher is a convenience fallback, not a guaranteed live feed. Verify current quotes and market-session state with a reputable source. Use `--exclude-last-bar` when the final daily row is incomplete.

The calculator also accepts third-party CSV files with case-insensitive columns for date, open, high, low, close, volume, and optional adjusted close.

## Test

```bash
python -m unittest discover -s tests -v
```

## Scope and risk

This repository performs analysis only. It does not place orders, manage brokerage credentials, or silently install dependencies.

This is a rules-based chart analysis workflow, not personalized financial advice.
