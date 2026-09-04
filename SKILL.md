---
name: oliver-kell-cpa
description: Analyze stocks and ETFs with Oliver Kell-style Cycle of Price Action (CPA). Use when the user says things like "用 CPA 帮我分析今天的 SNDK", "用 Cycle of Price Action 分析 NVDA", "analyze this ticker with CPA", or asks about Reversal Extension, Wedge Pop, EMA Crossback, Base & Break, Exhaustion Extension, or Wedge Drop.
---
# Oliver Kell Cycle of Price Action (CPA)
Use this skill for disciplined, data-grounded Cycle of Price Action analysis of stocks and ETFs.
The goal is not to improvise from generic technical-analysis knowledge. Always obtain real market data first, determine the current CPA stage, show evidence, define invalidation, and state uncertainty.
This skill is inspired by the public Oliver Kell / Cycle of Price Action framework. Numerical thresholds below are implementation heuristics for consistent agent behavior; do not attribute them to Oliver Kell as official rules.
## Triggers
Use this skill when the user:
- asks to analyze a ticker "with CPA";
- mentions "Cycle of Price Action" or Oliver Kell;
- asks which CPA stage a stock is in;
- asks whether a chart is Reversal Extension, Wedge Pop, EMA Crossback, Base & Break, Exhaustion Extension, or Wedge Drop;
- asks for a CPA entry, invalidation, stop, risk/reward, setup grade, or multi-ticker CPA screen.
Examples:
- `用 CPA 帮我分析今天的 SNDK。`
- `用 CPA 看一下 NVDA 现在是不是 EMA Crossback。`
- `Analyze MU with Oliver Kell's Cycle of Price Action.`
- `把 SNDK、MU、NVDA 按 CPA setup 从强到弱排序。`
Do not invoke CPA merely for a generic fundamental question.
## Core principles
1. Price structure is primary.
2. Volume confirms price.
3. Location in the cycle matters more than a pattern in isolation.
4. 10 EMA and 20 EMA define short-term trend.
5. 50 SMA and 200 SMA provide broader context.
6. Relative strength versus a benchmark matters.
7. Determine stage before discussing action.
8. Never fabricate live prices, indicators, volume, news, or levels.
9. An incomplete intraday daily bar is not a completed daily bar.
10. `NO CLEAN CPA SETUP` is a valid conclusion.
## Required data
For normal daily-chart analysis obtain:
- latest quote when available;
- at least 6 months of daily OHLCV, preferably 12 months;
- EMA10, EMA20, SMA50, SMA200;
- ATR(14);
- 20-day average volume;
- benchmark data for relative strength.
Default benchmark:
- growth / technology / high-beta stocks: `QQQ`;
- broad-market stocks: `SPY`;
- use a relevant sector ETF when clearly more appropriate.
For higher-quality context inspect:
- 1.5-3 years of weekly data;
- major prior highs/lows;
- gaps;
- recent earnings or major catalysts when they explain abnormal price/volume.
## Data-source policy
Use the best actual market-data source available:
1. market-data / finance tool;
2. web/browser access to a reputable market-data source;
3. configured brokerage or financial API;
4. local Python/data files.
If Python is available and a package such as `yfinance` is already installed, it may be used. Do not silently install packages, spend money, sign up for services, or use credentials without permission.
Always report:
- as-of date/time;
- market session when known: pre-market / regular / after-hours / closed;
- whether the newest daily bar is complete or intraday;
- sources used.
If the user says "today", resolve the actual current date. Never rely on model memory for a current analysis.
If live/current data cannot be obtained:
- do not invent an answer;
- do not claim a current CPA stage;
- state what is missing;
- if historical data exists, analyze only through the last available bar and state that date.
## Calculations
Use:
- `EMA10 = EMA(close, 10)`
- `EMA20 = EMA(close, 20)`
- `SMA50 = SMA(close, 50)`
- `SMA200 = SMA(close, 200)`
- `VOL20 = SMA(volume, 20)`
- `ATR14 = Wilder ATR(14)`
- `Ext10 = (Close - EMA10) / ATR14`
- `Ext20 = (Close - EMA20) / ATR14`
- `RelVol = Volume / VOL20`
Relative strength:
- compare ticker return versus benchmark over 20 trading days;
- compare ticker return versus benchmark over 63 trading days.
Do not confuse benchmark-relative strength with RSI. RSI is not required.
# CPA cycle
Primary stages:
1. Reversal Extension
2. Wedge Pop
3. EMA Crossback
4. Base & Break
5. Exhaustion Extension
6. Wedge Drop
A chart can be transitional. Return a primary stage, optional secondary/developing stage, and confidence. Never force a ticker into a stage.
## 1. Reversal Extension
Interpretation: a prior decline is stretched and price is attempting a reversal.
Evidence:
- clear preceding decline;
- price materially below declining/recently declining 10/20 EMA;
- negative extension, often near `Ext10 <= -1.5` or `Ext20 <= -2.0`;
- meaningful support, prior low, gap area, weekly level, or washout low;
- reversal candle, undercut-and-reclaim, strong close, or sharp rejection;
- volume expansion, ideally `RelVol >= 1.3`;
- selling appears climactic/exhausted.
Potential trigger:
- break above reversal-bar high or nearby pivot.
Invalidation:
- decisive loss of reversal low / setup support.
Do not call every oversold stock a Reversal Extension. A falling stock with no reversal evidence is simply weak.
## 2. Wedge Pop
Interpretation: after a reversal/early advance, price compresses and breaks upward as a new trend organizes.
Evidence:
- recent reversal or trend transition;
- roughly 3-10+ bars of tightening action / constructive higher lows / small wedge;
- range and/or volume contraction;
- 10 EMA flattening or turning higher;
- price reclaiming/holding 10/20 EMA;
- breakout above wedge/consolidation high;
- constructive breakout volume.
Potential trigger:
- break above wedge high.
Invalidation:
- failure back through wedge plus loss of setup low / EMA structure.
Prefer early-cycle Wedge Pops with limited overhead supply.
## 3. EMA Crossback
Interpretation: a confirmed uptrend pulls back toward rising 10/20 EMA and resumes.
This is a high-priority CPA setup.
Evidence:
- meaningful prior thrust;
- rising/improving EMA10 and EMA20;
- preferably `EMA10 > EMA20`;
- first or early pullback toward 10/20 EMA;
- price within roughly `0.5 ATR` of EMA10/EMA20, or briefly undercuts and reclaims;
- pullback volume contracts when possible;
- bullish reversal/resumption bar appears;
- relative strength remains constructive.
Penalize:
- repeated deep 20 EMA tests;
- flat/falling EMA20;
- heavy-volume closes below EMA20;
- obvious distribution.
Potential trigger:
- break above rebound/reversal bar or nearby pivot.
Invalidation:
- setup low or decisive loss of the EMA/support structure.
## 4. Base & Break
Interpretation: an established/emerging uptrend forms a base and breaks resistance.
Evidence:
- identifiable pivot/resistance;
- base usually ~10+ trading days; shorter flags can qualify in exceptional momentum;
- constructive consolidation;
- tightening ranges, higher lows, volatility contraction;
- supportive EMA20 and preferably SMA50;
- breakout above pivot;
- breakout volume ideally `RelVol >= 1.3`;
- strong/improving relative strength.
Penalize:
- repeated failed breakouts;
- wide/loose action;
- large overhead supply;
- breakout already extremely extended from 10/20 EMA;
- weak relative strength.
Potential trigger:
- break above base pivot.
Invalidation:
- failed breakout back into base or loss of structurally relevant support.
A late-stage base is not equivalent to an early-stage base.
## 5. Exhaustion Extension
Interpretation: a mature uptrend becomes abnormally stretched and may be climactic.
Evidence:
- mature prior advance;
- sharp acceleration;
- often `Ext10 >= +2.0` or `Ext20 >= +3.0`;
- consecutive wide-range up bars;
- gaps after an already extended move;
- very high relative volume;
- vertical/euphoric action;
- reversal wick or failed continuation.
Important:
- extension alone does not prove a top;
- this is mainly an avoid-chasing / risk-management condition;
- do not automatically short a strong stock.
For existing longs consider:
- trimming into strength;
- tightening risk;
- trailing with 10/20 EMA or a structurally relevant prior low.
For new entries:
- usually `WATCH / WAIT`, not chase.
## 6. Wedge Drop
Interpretation: a prior uptrend is losing control and breaks short-term trend support.
Evidence:
- mature/damaged prior uptrend;
- lower highs, topping wedge, failed breakout, or distribution;
- loss of EMA10 then EMA20;
- EMA10 rolling over;
- failed reclaim of EMA zone;
- distribution volume;
- weakening relative strength.
Strong version:
- breakdown through EMA20/important support;
- weak bounce;
- rejection at EMA10/EMA20;
- renewed selling.
For existing longs treat as defensive/exit risk. Do not automatically recommend a short unless the user explicitly wants bearish trading analysis.
# Trend context
Short-term bullish evidence:
- Close > EMA10;
- EMA10 > EMA20;
- EMA10 slope > 0;
- EMA20 slope > 0.
Intermediate constructive evidence:
- Close > SMA50;
- SMA50 slope > 0;
- pullbacks respect SMA50;
- RS stable/rising.
Long-term constructive evidence:
- Close > SMA200;
- SMA50 > SMA200.
Do not reject an early Reversal Extension/Wedge Pop merely because long-term averages have not yet turned up.
# Volume
Constructive:
- reversal/breakout volume expands;
- pullback volume contracts;
- accumulation appears near key levels.
Warnings:
- repeated heavy-volume down days;
- weak-volume breakout;
- high-volume failed breakout;
- climax volume after a mature run.
Always compare against recent volume, preferably VOL20.
# Relative strength
Check:
- 20-day performance versus benchmark;
- 63-day performance versus benchmark;
- whether RS is making highs while price bases;
- whether RS weakens before price breaks.
Prefer strong/improving RS. Weak RS lowers confidence but does not automatically invalidate an early reversal setup.
# Execution procedure
## Step 1 — Resolve request
Identify:
- ticker(s);
- exchange if ambiguous;
- timeframe;
- whether "today/current/now" requires live analysis;
- whether the user wants analysis only or also a trade plan.
Default:
- daily chart for primary classification;
- weekly chart for context.
Do not ask a question if the ticker can be resolved confidently.
## Step 2 — Fetch and validate
Fetch required data and check:
- newest trading date;
- stale quotes;
- missing sessions;
- splits;
- ticker/company changes;
- suspicious zero volume;
- incomplete current candle.
If a spin-off, relisting, merger, or IPO limits history, say so.
## Step 3 — Calculate
Calculate:
- EMA10, EMA20, SMA50, SMA200;
- ATR14, VOL20, RelVol;
- Ext10, Ext20;
- 20d and 63d benchmark-relative performance.
## Step 4 — Read structure
Identify:
- recent swing high/low;
- support/resistance;
- gaps;
- trending versus basing;
- range expansion/contraction;
- early/middle/late location within the larger move.
## Step 5 — Evaluate all stages
Evidence priority:
1. price structure;
2. location in broader trend;
3. 10/20 EMA behavior;
4. volume;
5. relative strength;
6. 50/200 SMA context;
7. catalyst context.
Choose:
- primary stage;
- optional secondary stage;
- confidence: High / Medium / Low.
High = structure and confirmations align.
Medium = plausible structure with missing confirmations.
Low = mixed/developing evidence.
## Step 6 — Define setup
When a valid setup exists identify:
- trigger / entry zone;
- invalidation;
- structural stop reference;
- risk distance in dollars and percent;
- nearby resistance;
- potential reward in R.
Never move a stop merely to manufacture attractive R/R.
Do not invent a fixed target. In strong trends, a 10/20 EMA trailing exit may be more appropriate.
## Step 7 — Grade quality
This is an internal rubric, not an official Oliver Kell grade.
Score 0-100:
- Price structure / stage clarity: 0-25
- EMA alignment / trend quality: 0-20
- Volume confirmation: 0-15
- Relative strength: 0-15
- Location / overhead supply: 0-15
- Risk definition / entry efficiency: 0-10
Grades:
- A+: 95-100
- A: 90-94
- A-: 85-89
- B+: 80-84
- B: 75-79
- B-: 70-74
- C: 60-69
- D: 50-59
- F: <50
A high grade means clean setup quality, not certainty of profit.
## Step 8 — Action state
Use exactly one:
- `BUYABLE NOW`
- `WATCH / WAIT FOR TRIGGER`
- `HOLD / TREND INTACT`
- `TRIM / EXTENDED`
- `DEFENSIVE / EXIT RISK`
- `NO CLEAN CPA SETUP`
Use `BUYABLE NOW` only if current data shows the trigger occurred and price is not materially extended.
# Single-ticker output
Respond in the user's language.
## <TICKER> — CPA Analysis
**As of:** <date/time + timezone>  
**Session:** <pre-market / regular / after-hours / closed>  
**Latest bar:** <complete / intraday>  
**Primary CPA stage:** <stage>  
**Secondary stage:** <stage or none>  
**Confidence:** <High / Medium / Low>  
**CPA setup grade:** <A+ ... F>  
**CPA action state:** <state>
### 1. Why this stage
Give 3-6 concrete observations tied to actual data. Include useful numerical evidence: price versus EMA10/20, extension, volume, pivot/support, RS.
### 2. Trend structure
| Item | Reading | Interpretation |
|---|---:|---|
| Price | ... | ... |
| 10 EMA | ... | ... |
| 20 EMA | ... | ... |
| 50 SMA | ... | ... |
| 200 SMA | ... | ... |
| ATR(14) | ... | ... |
| Relative Volume | ... | ... |
| 20d RS vs benchmark | ... | ... |
| 63d RS vs benchmark | ... | ... |
### 3. Key levels
- **Trigger / pivot:** ...
- **Preferred entry zone:** ...
- **Invalidation:** ...
- **Structural stop reference:** ...
- **Nearest support:** ...
- **Nearest resistance:** ...
If a level is not objectively identifiable, say so.
### 4. Risk / reward
When entry and stop exist:
- Entry reference: ...
- Stop reference: ...
- Risk/share: ...
- Risk %: ...
- 1R: ...
- 2R: ...
- 3R: ...
- Relevant chart resistance: ...
Explain whether resistance makes nominal R targets realistic.
### 5. Bull case vs failure case
**Bull case**
- 2-4 conditions that would confirm the setup.
**Failure case**
- 2-4 conditions that would invalidate/weaken it.
### 6. CPA verdict
Use a concise conclusion:
> `<TICKER> is currently best classified as ______. Under the CPA framework, the appropriate state is ______ because ______. The key level is ______; a break/hold of ______ would change the classification to ______.`
### Sources
List actual market-data/chart/news sources used.
End with:
`This is a rules-based chart analysis, not personalized financial advice.`
# Multi-ticker screener
For multiple tickers use the same data timestamp when possible.
| Rank | Ticker | CPA Stage | Grade | Action State | Trigger | Invalidation | RS | Key reason |
|---:|---|---|---|---|---:|---:|---|---|
Rank by:
- stage clarity;
- early/efficient location;
- RS;
- volume;
- clearly defined risk.
Do not rank a ticker higher merely because it has risen more.
Add brief notes for:
- top setups;
- Exhaustion Extension names;
- Wedge Drop names.
# Intraday handling
CPA here is primarily a daily/swing framework.
If "today" is requested during the U.S. session:
1. use the latest completed daily bar for stable indicator context;
2. use current intraday price/volume as provisional evidence;
3. label today's candle incomplete;
4. do not call a daily breakout confirmed before the close unless the user explicitly wants intraday execution.
Pre-market/after-hours:
- report extended-hours price separately;
- label extended-hours volume;
- treat pre-market breakouts as provisional.
# Earnings / gaps
When a major earnings/catalyst gap exists:
- identify it;
- state whether the gap is holding;
- measure extension after the gap;
- distinguish fresh institutional demand from late-stage exhaustion;
- do not call the stock buyable merely because it gapped up.
If earnings are imminent and known:
- mention event risk;
- do not assume chart stops protect against an earnings gap.
# Failure shields
## Stale-data shield
If the newest quote/date is old:
- verify latest trading date;
- state stale date;
- do not answer "today/current".
## Hallucinated-level shield
If a level cannot be traced to OHLC/EMA/pivot data:
- recompute it or remove it.
## Incomplete-candle shield
If today's daily candle is still trading:
- mark signals provisional;
- distinguish intraday price from close-confirmed signals.
## False-breakout shield
If price trades above a pivot but closes back inside:
- call it provisional/failed, not confirmed Base & Break.
## Late-stage-chase shield
If breakout occurs after a mature, highly extended run:
- consider Exhaustion Extension or late-stage Base & Break;
- prefer WAIT/TRIM over ideal fresh entry.
## Falling-knife shield
If price is far below EMAs but has no reversal evidence:
- do not label Reversal Extension solely because it is oversold.
## Benchmark-RS shield
Never claim "RS is strong" from absolute price alone:
- calculate versus QQQ/SPY/sector benchmark.
# Verification checklist
Before finalizing verify:
- [ ] Actual market data was used.
- [ ] As-of time/date is stated.
- [ ] Completed versus intraday bar is stated.
- [ ] EMA10 and EMA20 are verified/calculated.
- [ ] SMA50/SMA200 are checked when history allows.
- [ ] Volume is compared with recent history.
- [ ] Relative strength is checked versus a benchmark.
- [ ] Relevant CPA stages were evaluated.
- [ ] Stage selection is explained.
- [ ] Invalidation comes from chart structure.
- [ ] No target/level was fabricated.
- [ ] Confidence is reduced when evidence is mixed.
- [ ] Data sources are listed.
If actual current market data, as-of date, or EMA context cannot be established, do not claim a current CPA classification.
# Canonical example
User:
`用 CPA 帮我分析今天的 SNDK。`
Required workflow:
1. Resolve current date and U.S. market session.
2. Fetch current SNDK quote and daily OHLCV.
3. Fetch QQQ benchmark data.
4. Compute EMA10, EMA20, SMA50, SMA200, ATR14, VOL20, Ext10, Ext20, RelVol, 20d/63d RS.
5. Inspect price structure, support/resistance, gaps, and volume.
6. Evaluate all CPA stages.
7. Select primary stage + confidence.
8. Determine trigger, invalidation, risk, and setup grade.
9. Return the standard CPA report.
10. If today's bar is incomplete, label all current-day signals provisional.
Never answer the example from memory. Re-run the workflow using current data every time.
