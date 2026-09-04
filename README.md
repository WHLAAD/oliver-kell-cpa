# Oliver Kell CPA Skill

A portable Codex Skill for rules-based analysis of stocks and ETFs using an Oliver Kell-inspired Cycle of Price Action workflow.

This is an independent, unofficial implementation. Its numerical thresholds and setup grade are consistency heuristics, not rules attributed to Oliver Kell.

## What it provides

- Natural-language and explicit `$oliver-kell-cpa` invocation.
- Six-stage CPA classification guidance.
- Deterministic EMA, SMA, Wilder ATR, volume, extension, and benchmark-relative-strength calculations.
- A no-dependency market-data fallback for daily Yahoo Finance chart data.
- Full-report, trade-plan, intraday, and multi-ticker output conventions.
- Standard-library unit tests for the calculator.

## Repository layout

```text
oliver-kell-cpa/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── calculate_cpa.py
│   └── fetch_market_data.py
├── references/
│   ├── cpa-stages.md
│   └── reporting-and-risk.md
├── tests/test_calculate_cpa.py
└── README.md
```

## Install

Ask Codex to install the Skill from this repository:

```text
Use $skill-installer to install the Skill from
https://github.com/WHLAAD/oliver-kell-cpa
```

Restart Codex if the newly installed Skill does not appear immediately.

## Use

Natural language:

```text
用 CPA 帮我分析今天的 NVDA。
```

Explicit invocation:

```text
Use $oliver-kell-cpa to rank NVDA, MU, and AVGO by CPA setup quality.
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
