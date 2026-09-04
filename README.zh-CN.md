# 利用 Cycle of Price Action 分析股票

[English](README.md) | **简体中文**

这是一个可移植的 Codex Skill，使用价格行为周期（Cycle of Price Action，CPA）框架分析股票和 ETF。

这是一个独立、非官方的实现。其数值阈值和形态评级属于保持分析一致性的启发式方法，并非 Oliver Kell 本人制定或认可的规则。

## 策略背景

Cycle of Price Action 是由 2020 年美国投资锦标赛冠军 Oliver Kell 推广的一套主观型波段交易与趋势分析框架。它把股票的价格行为组织为一个循环序列：

`Reversal Extension → Wedge Pop → EMA Crossback → Base & Break → Exhaustion Extension → Wedge Drop`

该框架综合价格与成交量、10 和 20 周期指数移动平均线、更高时间周期背景、相对强弱、靠近明确支撑位的入场，以及趋势过度延伸或结构失效时的退出。Kell 将自己的整体方法描述为对 CAN SLIM 的改造，同时受到 William O'Neil、Jesse Livermore、Nicolas Darvas 和 Richard Wyckoff 的影响。参见 [CPA 官方介绍](https://kelltrading.com/)以及 *Victory in Stock Trading* 的[出版信息](https://books.google.com/books/about/Victory_in_Stock_Trading_Strategies_and.html?id=QhctEAAAQBAJ)。

## 历史业绩与年化收益

[2020 年 12 月官方榜单](https://financial-competitions.com/previousstandings/2021/1/13/december-2020-standings)显示，Oliver Kell 在截至 2020 年 12 月 31 日的美国投资锦标赛股票组取得了 **+941.1% 的收益率**。该比赛按照公开的[比赛规则](https://financial-competitions.com/rules)跟踪指定的真实资金账户。

这个数字是一届比赛年度内的单年成绩，不是多年复合年化收益率，也不是对所有 CPA 信号进行回测所得的结果，更不是使用本 Skill 可以预期获得的收益。本仓库没有经过独立验证的长期业绩记录，因此**不会声称 CPA 能够稳定实现某个固定年化收益率**。要形成可信的收益预期，需要先明确完整的交易规则和仓位管理方式，并在计入交易成本、滑点、生存者偏差的情况下进行样本外回测和回撤分析。2020 年的成绩属于极端优秀的个案，不应直接用作投资规划假设；历史业绩不代表未来表现。

## 功能

- 支持自然语言和显式 `$cycle-of-price-action` 调用。
- 提供六阶段 CPA 分类指引。
- 确定性计算 EMA、SMA、Wilder ATR、成交量、价格延伸度和相对基准强弱。
- 提供无需第三方依赖的 Yahoo Finance 日线行情备用获取方式。
- 规定完整报告、交易计划、盘中分析和多标的筛选的输出方式。
- 为指标计算器提供仅使用 Python 标准库的单元测试。

## 仓库结构

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

## 安装

让 Codex 从此仓库安装该 Skill：

```text
使用 $skill-installer 从以下仓库安装 Skill：
https://github.com/WHLAAD/cycle-of-price-action
```

如果新安装的 Skill 没有立即出现，请重启 Codex。

## 使用

自然语言调用：

```text
用 CPA 框架分析今天的 NVDA。
```

显式调用：

```text
使用 $cycle-of-price-action，按照 CPA 形态质量对 NVDA、MU 和 AVGO 进行排名。
```

## 确定性计算流程

脚本要求 Python 3.10 或更高版本，并且只使用标准库。

```bash
python scripts/fetch_market_data.py NVDA QQQ --start 2025-01-01 --output-dir .tmp/cpa-data
python scripts/calculate_cpa.py \
  --symbol NVDA --symbol-csv .tmp/cpa-data/NVDA_daily.csv \
  --benchmark QQQ --benchmark-csv .tmp/cpa-data/QQQ_daily.csv \
  --output .tmp/cpa-data/NVDA_cpa.json
```

行情获取脚本只是备用工具，并不保证提供实时数据。请使用可靠来源核对最新报价和市场交易时段状态。当最后一条日线尚未收盘时，请使用 `--exclude-last-bar`。

指标计算器也支持第三方 CSV 文件；列名不区分大小写，需包含日期、开盘价、最高价、最低价、收盘价和成交量，也可以包含复权收盘价。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 范围与风险

本仓库只执行分析，不会下单、管理券商凭据或静默安装依赖。

这是基于规则的图表分析流程，不构成个性化投资建议。
