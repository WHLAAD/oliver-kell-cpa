#!/usr/bin/env python3
"""Fetch split-adjusted daily OHLCV data with no third-party dependencies.

This is a convenience fallback for the Oliver Kell CPA Skill. It uses Yahoo
Finance's public chart endpoint and writes normalized CSV plus provenance JSON.
The endpoint can be delayed, rate-limited, or unavailable; current values still
need session-aware verification before they are described as live.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
USER_AGENT = "oliver-kell-cpa/1.0 (portable Codex skill)"
SYMBOL_PATTERN = re.compile(r"^[A-Za-z0-9.\-^=]{1,32}$")


class FetchError(RuntimeError):
    """Raised when a provider response cannot produce trustworthy rows."""


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid ISO date: {value}") from exc


def epoch_seconds(value: date) -> int:
    return int(datetime.combine(value, time.min, tzinfo=timezone.utc).timestamp())


def build_url(symbol: str, start: date, end: date) -> str:
    query = urllib.parse.urlencode(
        {
            "period1": epoch_seconds(start),
            "period2": epoch_seconds(end + timedelta(days=1)),
            "interval": "1d",
            "events": "div,splits",
            "includeAdjustedClose": "true",
            "includePrePost": "false",
        }
    )
    return f"{API_URL.format(symbol=urllib.parse.quote(symbol))}?{query}"


def request_json(url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise FetchError(f"HTTP {exc.code} from Yahoo Finance") from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"Network error: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise FetchError("Yahoo Finance returned invalid JSON") from exc


def exchange_datetime(timestamp: int, timezone_name: str | None) -> datetime:
    value = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    if timezone_name:
        try:
            return value.astimezone(ZoneInfo(timezone_name))
        except ZoneInfoNotFoundError:
            pass
    return value


def adjusted_value(value: Any, factor: float) -> float | None:
    if value is None:
        return None
    return float(value) * factor


def parse_chart(payload: dict[str, Any], requested_symbol: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    chart = payload.get("chart") or {}
    provider_error = chart.get("error")
    if provider_error:
        description = provider_error.get("description") or str(provider_error)
        raise FetchError(description)

    results = chart.get("result") or []
    if not results:
        raise FetchError("Yahoo Finance returned no chart result")

    result = results[0]
    metadata = result.get("meta") or {}
    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators") or {}
    quotes = indicators.get("quote") or []
    if not timestamps or not quotes:
        raise FetchError("Yahoo Finance returned no daily OHLCV rows")

    quote = quotes[0]
    adjusted_sets = indicators.get("adjclose") or []
    adjusted_closes = adjusted_sets[0].get("adjclose", []) if adjusted_sets else []
    timezone_name = metadata.get("exchangeTimezoneName")
    rows: list[dict[str, Any]] = []

    for index, timestamp in enumerate(timestamps):
        raw_close = _at(quote.get("close"), index)
        raw_open = _at(quote.get("open"), index)
        raw_high = _at(quote.get("high"), index)
        raw_low = _at(quote.get("low"), index)
        volume = _at(quote.get("volume"), index)
        if None in (raw_open, raw_high, raw_low, raw_close):
            continue

        adj_close = _at(adjusted_closes, index)
        factor = float(adj_close) / float(raw_close) if adj_close is not None and float(raw_close) != 0 else 1.0
        row_date = exchange_datetime(int(timestamp), timezone_name).date().isoformat()
        rows.append(
            {
                "date": row_date,
                "open": adjusted_value(raw_open, factor),
                "high": adjusted_value(raw_high, factor),
                "low": adjusted_value(raw_low, factor),
                "close": adjusted_value(raw_close, factor),
                "adj_close": float(adj_close) if adj_close is not None else float(raw_close),
                "raw_close": float(raw_close),
                "volume": int(volume) if volume is not None else 0,
            }
        )

    rows.sort(key=lambda row: row["date"])
    deduplicated = {row["date"]: row for row in rows}
    rows = list(deduplicated.values())
    if not rows:
        raise FetchError("All returned rows were incomplete")

    provenance = {
        "schema_version": "1.0",
        "provider": "Yahoo Finance chart API",
        "requested_symbol": requested_symbol,
        "resolved_symbol": metadata.get("symbol") or requested_symbol,
        "currency": metadata.get("currency"),
        "exchange": metadata.get("fullExchangeName") or metadata.get("exchangeName"),
        "exchange_timezone": timezone_name,
        "instrument_type": metadata.get("instrumentType"),
        "regular_market_price": metadata.get("regularMarketPrice"),
        "regular_market_time": _format_timestamp(metadata.get("regularMarketTime"), timezone_name),
        "previous_close": metadata.get("chartPreviousClose") or metadata.get("previousClose"),
        "fifty_two_week_high": metadata.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": metadata.get("fiftyTwoWeekLow"),
        "first_bar_date": rows[0]["date"],
        "last_bar_date": rows[-1]["date"],
        "bar_count": len(rows),
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "notice": "Best-effort fallback data. Verify current quotes and session state and final-bar completeness independently.",
    }
    return rows, provenance


def _at(values: Any, index: int) -> Any:
    if not isinstance(values, list) or index >= len(values):
        return None
    return values[index]


def _format_timestamp(value: Any, timezone_name: str | None) -> str | None:
    if value is None:
        return None
    try:
        return exchange_datetime(int(value), timezone_name).isoformat()
    except (TypeError, ValueError, OSError):
        return None


def safe_stem(symbol: str) -> str:
    return symbol.upper().replace("^", "INDEX_").replace("=", "_")


def write_symbol(output_dir: Path, symbol: str, rows: list[dict[str, Any]], metadata: dict[str, Any]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_stem(symbol)
    csv_path = output_dir / f"{stem}_daily.csv"
    metadata_path = output_dir / f"{stem}_metadata.json"
    fields = ["date", "open", "high", "low", "close", "adj_close", "raw_close", "volume"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return csv_path, metadata_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    today = datetime.now(timezone.utc).date()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("symbols", nargs="+", help="Ticker symbols, for example NVDA QQQ")
    parser.add_argument("--start", type=parse_iso_date, default=today - timedelta(days=800), help="First calendar date (YYYY-MM-DD)")
    parser.add_argument("--end", type=parse_iso_date, default=today, help="Last calendar date, inclusive (YYYY-MM-DD)")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for normalized CSV and metadata JSON")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.start > args.end:
        print("error: --start must not be after --end", file=sys.stderr)
        return 2

    failures = 0
    for original_symbol in args.symbols:
        symbol = original_symbol.strip().upper()
        if not SYMBOL_PATTERN.fullmatch(symbol):
            print(f"error: invalid symbol {original_symbol!r}", file=sys.stderr)
            failures += 1
            continue
        try:
            url = build_url(symbol, args.start, args.end)
            rows, metadata = parse_chart(request_json(url, args.timeout), symbol)
            csv_path, metadata_path = write_symbol(args.output_dir, symbol, rows, metadata)
            print(f"{symbol}: {len(rows)} bars -> {csv_path}")
            print(f"{symbol}: metadata -> {metadata_path}")
        except (FetchError, OSError) as exc:
            print(f"error: {symbol}: {exc}", file=sys.stderr)
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
