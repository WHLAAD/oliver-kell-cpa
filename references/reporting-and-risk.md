# CPA reporting and risk reference

Use this reference for full single-ticker reports, trade plans, grades, intraday analysis, and multi-ticker screens.

## Setup quality grade

This is an internal rubric, not an official Oliver Kell grade.

- Price structure and stage clarity: 0-25.
- EMA alignment and trend quality: 0-20.
- Volume confirmation: 0-15.
- Benchmark-relative strength: 0-15.
- Cycle location and overhead supply: 0-15.
- Risk definition and entry efficiency: 0-10.

Map totals to grades:

- A+: 95-100
- A: 90-94
- A-: 85-89
- B+: 80-84
- B: 75-79
- B-: 70-74
- C: 60-69
- D: 50-59
- F: below 50

A high grade means clean setup quality, not certainty of profit.

## Risk and reward

When both an entry reference and structural stop exist, report entry, stop, risk per share, risk percent, and 1R/2R/3R prices. Compare nominal R levels with actual chart resistance; do not imply that a mathematical R target is realistic when major resistance intervenes.

Keep trigger, invalidation, and stop conceptually distinct:

- Trigger: observable event that activates the setup.
- Invalidation: chart evidence that disproves or materially weakens the setup.
- Stop reference: a possible execution level derived from structure, which may be tighter than thesis invalidation.

Do not personalize position size without the user's portfolio constraints. Do not imply that chart stops protect against earnings gaps.

## Single-ticker report

Use this shape when the user wants a full analysis:

```markdown
## <TICKER> — CPA Analysis

**As of:** <date/time + timezone>
**Session:** <pre-market / regular / after-hours / closed>
**Latest bar:** <date and complete/intraday>
**Primary CPA stage:** <stage>
**Secondary stage:** <stage or none>
**Confidence:** <High / Medium / Low>
**CPA setup grade:** <A+ ... F>
**CPA action state:** <one allowed state>

### Why this stage
<3-6 concrete observations tied to actual data>

### Trend structure
| Item | Reading | Interpretation |
|---|---:|---|
| Price | ... | ... |
| EMA10 | ... | ... |
| EMA20 | ... | ... |
| SMA50 | ... | ... |
| SMA200 | ... | ... |
| ATR(14) | ... | ... |
| Relative volume | ... | ... |
| 20d RS vs benchmark | ... | ... |
| 63d RS vs benchmark | ... | ... |

### Key levels
- Trigger / pivot: ...
- Preferred entry area: ...
- Invalidation: ...
- Structural stop reference: ...
- Nearest support: ...
- Nearest resistance: ...

### Risk / reward
<entry, stop, risk/share, risk %, R levels, and intervening resistance>

### Bull case vs failure case
<2-4 observable conditions for each>

### CPA verdict
<concise classification, action, key level, and what would change the stage>

### Sources
<actual market-data, chart, and catalyst sources>
```

If an objective level does not exist, say so. End with the required financial-analysis disclaimer from `SKILL.md`.

## Multi-ticker screen

Use the same timestamp and benchmark convention when possible.

| Rank | Ticker | CPA stage | Grade | Action state | Trigger | Invalidation | RS | Key reason |
|---:|---|---|---|---|---:|---:|---|---|

Rank by stage clarity, early and efficient location, relative strength, volume confirmation, and clearly defined risk. Do not rank a ticker higher merely because it has risen more. Add brief notes for the strongest setups and any Exhaustion Extension or Wedge Drop names.

## Intraday and extended-hours handling

CPA is primarily a daily and swing framework.

During the U.S. session:

1. Use the latest completed daily bar for stable indicators.
2. Present current intraday price and volume separately as provisional.
3. Label today's daily candle incomplete.
4. Do not confirm a daily breakout before the close unless the user explicitly wants intraday execution analysis.

Pre-market and after-hours prices and volume must be labeled separately. Treat extended-hours breakouts as provisional.

## Earnings and gaps

When a major catalyst gap exists, identify the catalyst, state whether the gap is holding, measure extension, and distinguish fresh institutional demand from late-stage exhaustion. Do not label a stock buyable merely because it gapped up. If earnings are imminent and known, mention event risk.

## Failure shields

- Stale data: state the stale date and do not answer a current question as though data were live.
- Hallucinated level: recompute any level that cannot be traced to OHLC, an average, a gap, or a pivot.
- Incomplete candle: keep all current-day signals provisional.
- False breakout: if price trades above a pivot but closes back inside, call it provisional or failed.
- Late-stage chase: after a mature and extended run, prefer wait or trim over a fresh ideal-entry label.
- Falling knife: oversold conditions alone do not establish Reversal Extension.
- Relative strength: calculate performance versus the benchmark; absolute price appreciation is insufficient.
