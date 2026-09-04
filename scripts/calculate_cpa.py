#!/usr/bin/env python3
"""Calculate deterministic evidence for an Oliver Kell-style CPA analysis.

The script intentionally does not assign a CPA stage. It validates daily OHLCV,
calculates indicators and relative strength, and emits JSON evidence for an agent
to interpret alongside actual chart structure and market-session context.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Bar:
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class DataError(ValueError):
    """Raised when input data cannot support reliable calculations."""


def normalized_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def parse_date(value: str) -> date:
    cleaned = value.strip()
    if not cleaned:
        raise DataError("empty date")
    try:
        return date.fromisoformat(cleaned[:10])
    except ValueError as exc:
        raise DataError(f"invalid date {value!r}") from exc


def parse_number(value: Any, field: str) -> float:
    cleaned = str(value).replace(",", "").strip()
    if not cleaned or cleaned.lower() in {"null", "none", "nan", "n/a", "-"}:
        raise DataError(f"missing {field}")
    try:
        number = float(cleaned)
    except ValueError as exc:
        raise DataError(f"invalid {field}: {value!r}") from exc
    if not math.isfinite(number):
        raise DataError(f"non-finite {field}: {value!r}")
    return number


def resolve_columns(fieldnames: Iterable[str] | None) -> dict[str, str]:
    if not fieldnames:
        raise DataError("CSV has no header")
    normalized = {normalized_header(name): name for name in fieldnames}
    aliases = {
        "date": ("date", "datetime", "timestamp"),
        "open": ("open",),
        "high": ("high",),
        "low": ("low",),
        "close": ("close",),
        "adj_close": ("adj_close", "adjusted_close", "adjclose"),
        "volume": ("volume", "vol"),
    }
    resolved: dict[str, str] = {}
    for canonical, candidates in aliases.items():
        for candidate in candidates:
            if candidate in normalized:
                resolved[canonical] = normalized[candidate]
                break
    missing = [name for name in ("date", "open", "high", "low", "close", "volume") if name not in resolved]
    if missing:
        raise DataError(f"CSV is missing required columns: {', '.join(missing)}")
    return resolved


def load_bars(path: Path, as_of: date | None = None, exclude_last_bar: bool = False) -> list[Bar]:
    if not path.is_file():
        raise DataError(f"CSV does not exist: {path}")
    by_date: dict[date, Bar] = {}
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = resolve_columns(reader.fieldnames)
        for line_number, row in enumerate(reader, start=2):
            try:
                row_date = parse_date(row[columns["date"]])
                if as_of and row_date > as_of:
                    continue
                raw_open = parse_number(row[columns["open"]], "open")
                raw_high = parse_number(row[columns["high"]], "high")
                raw_low = parse_number(row[columns["low"]], "low")
                raw_close = parse_number(row[columns["close"]], "close")
                raw_volume = parse_number(row[columns["volume"]], "volume")
                factor = 1.0
                if "adj_close" in columns:
                    adjusted_text = str(row.get(columns["adj_close"], "")).strip()
                    if adjusted_text and adjusted_text.lower() not in {"null", "none", "nan", "n/a", "-"}:
                        adjusted_close = parse_number(adjusted_text, "adj_close")
                        if raw_close == 0:
                            raise DataError("close is zero and cannot be adjusted")
                        factor = adjusted_close / raw_close
                open_value = raw_open * factor
                high_value = raw_high * factor
                low_value = raw_low * factor
                close_value = raw_close * factor
                volume = int(round(raw_volume))
                if min(open_value, high_value, low_value, close_value) <= 0:
                    raise DataError("OHLC values must be positive")
                if high_value < max(open_value, low_value, close_value) or low_value > min(open_value, high_value, close_value):
                    raise DataError("OHLC range is inconsistent")
                if volume < 0:
                    raise DataError("volume must not be negative")
                by_date[row_date] = Bar(row_date, open_value, high_value, low_value, close_value, volume)
            except (DataError, KeyError) as exc:
                raise DataError(f"{path}:{line_number}: {exc}") from exc

    bars = [by_date[key] for key in sorted(by_date)]
    if exclude_last_bar and bars:
        bars.pop()
    if len(bars) < 20:
        raise DataError(f"At least 20 completed bars are required; found {len(bars)} in {path}")
    return bars


def ema(values: list[float], span: int) -> list[float]:
    alpha = 2.0 / (span + 1.0)
    output = [values[0]]
    for value in values[1:]:
        output.append(alpha * value + (1.0 - alpha) * output[-1])
    return output


def sma(values: list[float], window: int) -> list[float | None]:
    output: list[float | None] = [None] * len(values)
    running = 0.0
    for index, value in enumerate(values):
        running += value
        if index >= window:
            running -= values[index - window]
        if index >= window - 1:
            output[index] = running / window
    return output


def wilder_atr(bars: list[Bar], period: int = 14) -> list[float | None]:
    true_ranges: list[float] = []
    for index, bar in enumerate(bars):
        if index == 0:
            true_ranges.append(bar.high - bar.low)
        else:
            previous_close = bars[index - 1].close
            true_ranges.append(max(bar.high - bar.low, abs(bar.high - previous_close), abs(bar.low - previous_close)))

    output: list[float | None] = [None] * len(bars)
    if len(bars) < period:
        return output
    output[period - 1] = sum(true_ranges[:period]) / period
    for index in range(period, len(bars)):
        previous = output[index - 1]
        assert previous is not None
        output[index] = ((previous * (period - 1)) + true_ranges[index]) / period
    return output


def safe_divide(numerator: float, denominator: float | None) -> float | None:
    if denominator is None or denominator == 0:
        return None
    return numerator / denominator


def difference(values: list[float | None], periods: int) -> float | None:
    if len(values) <= periods or values[-1] is None or values[-1 - periods] is None:
        return None
    return float(values[-1]) - float(values[-1 - periods])


def percent_from(value: float, reference: float | None) -> float | None:
    ratio = safe_divide(value, reference)
    return None if ratio is None else (ratio - 1.0) * 100.0


def rolling_range(bars: list[Bar], window: int, exclude_latest: bool = False) -> dict[str, float] | None:
    source = bars[:-1] if exclude_latest else bars
    if not source:
        return None
    subset = source[-window:]
    return {"high": max(bar.high for bar in subset), "low": min(bar.low for bar in subset)}


def relative_strength(symbol_bars: list[Bar], benchmark_bars: list[Bar], periods: int) -> dict[str, Any]:
    benchmark_by_date = {bar.date: bar.close for bar in benchmark_bars}
    pairs = [(bar.date, bar.close, benchmark_by_date[bar.date]) for bar in symbol_bars if bar.date in benchmark_by_date]
    if len(pairs) <= periods:
        return {
            "periods": periods,
            "symbol_return_pct": None,
            "benchmark_return_pct": None,
            "excess_return_percentage_points": None,
            "relative_ratio_change_pct": None,
            "start_date": None,
            "end_date": pairs[-1][0].isoformat() if pairs else None,
        }
    start = pairs[-1 - periods]
    end = pairs[-1]
    symbol_return = end[1] / start[1] - 1.0
    benchmark_return = end[2] / start[2] - 1.0
    return {
        "periods": periods,
        "symbol_return_pct": symbol_return * 100.0,
        "benchmark_return_pct": benchmark_return * 100.0,
        "excess_return_percentage_points": (symbol_return - benchmark_return) * 100.0,
        "relative_ratio_change_pct": ((1.0 + symbol_return) / (1.0 + benchmark_return) - 1.0) * 100.0,
        "start_date": start[0].isoformat(),
        "end_date": end[0].isoformat(),
    }


def recent_gaps(bars: list[Bar], lookback: int = 63, minimum_abs_pct: float = 2.0) -> list[dict[str, Any]]:
    start_index = max(1, len(bars) - lookback)
    gaps: list[dict[str, Any]] = []
    for index in range(start_index, len(bars)):
        previous = bars[index - 1]
        current = bars[index]
        gap_pct = (current.open / previous.close - 1.0) * 100.0
        if abs(gap_pct) >= minimum_abs_pct:
            gaps.append(
                {
                    "date": current.date.isoformat(),
                    "gap_pct": gap_pct,
                    "open": current.open,
                    "previous_close": previous.close,
                    "held_at_close": current.close >= previous.close if gap_pct > 0 else current.close <= previous.close,
                }
            )
    return gaps[-10:]


def weekly_bars(bars: list[Bar], count: int = 12) -> list[dict[str, Any]]:
    grouped: dict[date, dict[str, Any]] = {}
    for bar in bars:
        week_ending = bar.date + timedelta(days=4 - bar.date.weekday())
        if week_ending not in grouped:
            grouped[week_ending] = {
                "week_ending": week_ending.isoformat(),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
        else:
            item = grouped[week_ending]
            item["high"] = max(item["high"], bar.high)
            item["low"] = min(item["low"], bar.low)
            item["close"] = bar.close
            item["volume"] += bar.volume
    return [grouped[key] for key in sorted(grouped)][-count:]


def serializable_bar(bar: Bar) -> dict[str, Any]:
    item = asdict(bar)
    item["date"] = bar.date.isoformat()
    return item


def build_report(symbol: str, symbol_bars: list[Bar], benchmark: str, benchmark_bars: list[Bar]) -> dict[str, Any]:
    closes = [bar.close for bar in symbol_bars]
    volumes = [float(bar.volume) for bar in symbol_bars]
    ema10 = ema(closes, 10)
    ema20 = ema(closes, 20)
    sma50 = sma(closes, 50)
    sma200 = sma(closes, 200)
    atr14 = wilder_atr(symbol_bars, 14)
    vol20 = sma(volumes, 20)
    latest = symbol_bars[-1]
    latest_atr = atr14[-1]
    latest_vol20 = vol20[-1]
    latest_ema10 = ema10[-1]
    latest_ema20 = ema20[-1]
    warnings: list[str] = []

    if len(symbol_bars) < 200:
        warnings.append("Fewer than 200 bars are available; SMA200 is unavailable.")
    if symbol_bars[-1].date != benchmark_bars[-1].date:
        warnings.append(
            f"Symbol and benchmark end on different dates: {symbol_bars[-1].date} vs {benchmark_bars[-1].date}."
        )
    if any(bar.volume == 0 for bar in symbol_bars[-20:]):
        warnings.append("At least one of the latest 20 symbol bars has zero volume.")
    age_days = (datetime.now(timezone.utc).date() - latest.date).days
    if age_days > 7:
        warnings.append(f"The latest symbol bar is {age_days} calendar days old and may be stale.")
    warnings.append("CSV data alone cannot prove that the newest daily bar is complete; verify the market session independently.")

    recent_rows: list[dict[str, Any]] = []
    start = max(0, len(symbol_bars) - 20)
    for index in range(start, len(symbol_bars)):
        bar = symbol_bars[index]
        current_atr = atr14[index]
        current_vol20 = vol20[index]
        recent_rows.append(
            {
                **serializable_bar(bar),
                "ema10": ema10[index],
                "ema20": ema20[index],
                "sma50": sma50[index],
                "sma200": sma200[index],
                "atr14": current_atr,
                "relative_volume": safe_divide(float(bar.volume), current_vol20),
                "ext10_atr": safe_divide(bar.close - ema10[index], current_atr),
                "ext20_atr": safe_divide(bar.close - ema20[index], current_atr),
            }
        )

    report = {
        "schema_version": "1.0",
        "symbol": symbol.upper(),
        "benchmark": benchmark.upper(),
        "as_of": latest.date.isoformat(),
        "latest_bar": serializable_bar(latest),
        "trend": {
            "ema10": latest_ema10,
            "ema20": latest_ema20,
            "sma50": sma50[-1],
            "sma200": sma200[-1],
            "ema10_slope_5d": difference(ema10, 5),
            "ema20_slope_5d": difference(ema20, 5),
            "sma50_slope_5d": difference(sma50, 5),
            "sma200_slope_5d": difference(sma200, 5),
            "close_vs_ema10_pct": percent_from(latest.close, latest_ema10),
            "close_vs_ema20_pct": percent_from(latest.close, latest_ema20),
            "close_vs_sma50_pct": percent_from(latest.close, sma50[-1]),
            "close_vs_sma200_pct": percent_from(latest.close, sma200[-1]),
        },
        "volatility_and_volume": {
            "atr14": latest_atr,
            "vol20": latest_vol20,
            "relative_volume": safe_divide(float(latest.volume), latest_vol20),
            "breakout_volume_1_3x": None if latest_vol20 is None else latest_vol20 * 1.3,
            "ext10_atr": safe_divide(latest.close - latest_ema10, latest_atr),
            "ext20_atr": safe_divide(latest.close - latest_ema20, latest_atr),
        },
        "relative_strength": {
            "20d": relative_strength(symbol_bars, benchmark_bars, 20),
            "63d": relative_strength(symbol_bars, benchmark_bars, 63),
        },
        "ranges": {
            "10d": rolling_range(symbol_bars, 10),
            "20d": rolling_range(symbol_bars, 20),
            "50d": rolling_range(symbol_bars, 50),
            "252d": rolling_range(symbol_bars, 252),
            "prior_10d_excluding_latest": rolling_range(symbol_bars, 10, exclude_latest=True),
            "prior_20d_excluding_latest": rolling_range(symbol_bars, 20, exclude_latest=True),
        },
        "recent_gaps": recent_gaps(symbol_bars),
        "weekly_context": weekly_bars(symbol_bars),
        "recent_daily_bars": recent_rows,
        "data_quality": {
            "symbol_bar_count": len(symbol_bars),
            "benchmark_bar_count": len(benchmark_bars),
            "symbol_first_date": symbol_bars[0].date.isoformat(),
            "symbol_last_date": symbol_bars[-1].date.isoformat(),
            "benchmark_first_date": benchmark_bars[0].date.isoformat(),
            "benchmark_last_date": benchmark_bars[-1].date.isoformat(),
            "latest_age_calendar_days": age_days,
            "warnings": warnings,
        },
    }
    return round_floats(report)


def round_floats(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, list):
        return [round_floats(item) for item in value]
    if isinstance(value, dict):
        return {key: round_floats(item) for key, item in value.items()}
    return value


def iso_date_argument(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid ISO date: {value}") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="Analyzed ticker")
    parser.add_argument("--symbol-csv", type=Path, required=True, help="Daily OHLCV CSV for the analyzed ticker")
    parser.add_argument("--benchmark", default="QQQ", help="Benchmark ticker")
    parser.add_argument("--benchmark-csv", type=Path, required=True, help="Daily OHLCV CSV for the benchmark")
    parser.add_argument("--as-of", type=iso_date_argument, help="Ignore rows after this date")
    parser.add_argument(
        "--exclude-last-bar",
        action="store_true",
        help="Drop the final row from both CSV files when the newest daily candle is incomplete",
    )
    parser.add_argument("--output", type=Path, help="Write JSON to this path instead of stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        symbol_bars = load_bars(args.symbol_csv, args.as_of, args.exclude_last_bar)
        benchmark_bars = load_bars(args.benchmark_csv, args.as_of, args.exclude_last_bar)
        report = build_report(args.symbol, symbol_bars, args.benchmark, benchmark_bars)
        report["provenance"] = {
            "symbol_csv": str(args.symbol_csv.resolve()),
            "benchmark_csv": str(args.benchmark_csv.resolve()),
            "as_of_filter": args.as_of.isoformat() if args.as_of else None,
            "excluded_last_bar": args.exclude_last_bar,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
            print(args.output)
        else:
            sys.stdout.write(rendered)
        return 0
    except (DataError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
