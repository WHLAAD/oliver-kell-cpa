# Oliver Kell CPA Skill

[English](README.md) | **简体中文**

这是一个可移植的 Codex Skill，使用受 Oliver Kell 启发的价格行为周期（Cycle of Price Action，CPA）工作流，对股票和 ETF 进行基于规则的分析。

这是一个独立、非官方的实现。其数值阈值和形态评级属于保持分析一致性的启发式方法，并非 Oliver Kell 本人制定或认可的规则。

## 功能

- 支持自然语言和显式 `$oliver-kell-cpa` 调用。
- 提供六阶段 CPA 分类指引。
- 确定性计算 EMA、SMA、Wilder ATR、成交量、价格延伸度和相对基准强弱。
- 提供无需第三方依赖的 Yahoo Finance 日线行情备用获取方式。
- 规定完整报告、交易计划、盘中分析和多标的筛选的输出方式。
- 为指标计算器提供仅使用 Python 标准库的单元测试。

## 仓库结构

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
├── README.md
└── README.zh-CN.md
```

## 安装

让 Codex 从此仓库安装该 Skill：

```text
使用 $skill-installer 从以下仓库安装 Skill：
https://github.com/WHLAAD/oliver-kell-cpa
```

如果新安装的 Skill 没有立即出现，请重启 Codex。

## 使用

自然语言调用：

```text
用 CPA 框架分析今天的 NVDA。
```

显式调用：

```text
使用 $oliver-kell-cpa，按照 CPA 形态质量对 NVDA、MU 和 AVGO 进行排名。
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
