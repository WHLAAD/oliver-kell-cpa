from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "calculate_cpa.py"
SPEC = importlib.util.spec_from_file_location("calculate_cpa", SCRIPT_PATH)
assert SPEC and SPEC.loader
calculate_cpa = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = calculate_cpa
SPEC.loader.exec_module(calculate_cpa)


def trading_dates(start: date, count: int) -> list[date]:
    values: list[date] = []
    current = start
    while len(values) < count:
        if current.weekday() < 5:
            values.append(current)
        current += timedelta(days=1)
    return values


def write_series(path: Path, closes: list[float], volumes: list[int] | None = None) -> None:
    dates = trading_dates(date(2025, 1, 2), len(closes))
    volumes = volumes or [1_000_000 + index * 1_000 for index in range(len(closes))]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"],
        )
        writer.writeheader()
        for index, close in enumerate(closes):
            open_value = close - 0.2
            writer.writerow(
                {
                    "Date": dates[index].isoformat(),
                    "Open": open_value,
                    "High": close + 1.0,
                    "Low": open_value - 1.0,
                    "Close": close,
                    "Adj Close": close,
                    "Volume": volumes[index],
                }
            )


class CalculateCpaTests(unittest.TestCase):
    def test_build_report_has_full_indicators_and_positive_relative_strength(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            symbol_path = root / "symbol.csv"
            benchmark_path = root / "benchmark.csv"
            symbol_closes = [100.0 + index * 0.55 + (index % 7) * 0.05 for index in range(260)]
            benchmark_closes = [300.0 + index * 0.20 for index in range(260)]
            write_series(symbol_path, symbol_closes)
            write_series(benchmark_path, benchmark_closes)

            symbol_bars = calculate_cpa.load_bars(symbol_path)
            benchmark_bars = calculate_cpa.load_bars(benchmark_path)
            report = calculate_cpa.build_report("TEST", symbol_bars, "QQQ", benchmark_bars)

            self.assertEqual(report["data_quality"]["symbol_bar_count"], 260)
            self.assertIsNotNone(report["trend"]["sma200"])
            self.assertGreater(report["latest_bar"]["close"], report["trend"]["ema10"])
            self.assertGreater(report["volatility_and_volume"]["atr14"], 0)
            self.assertGreater(
                report["relative_strength"]["63d"]["excess_return_percentage_points"],
                0,
            )
            self.assertLessEqual(
                report["ranges"]["prior_20d_excluding_latest"]["high"],
                report["ranges"]["20d"]["high"],
            )

    def test_adjusted_close_scales_ohlc(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "adjusted.csv"
            dates = trading_dates(date(2026, 1, 2), 20)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["date", "open", "high", "low", "close", "adj_close", "volume"],
                )
                writer.writeheader()
                for index, value_date in enumerate(dates):
                    raw_close = 100.0 + index
                    writer.writerow(
                        {
                            "date": value_date.isoformat(),
                            "open": raw_close - 1,
                            "high": raw_close + 2,
                            "low": raw_close - 2,
                            "close": raw_close,
                            "adj_close": raw_close / 2,
                            "volume": 1000,
                        }
                    )
            bars = calculate_cpa.load_bars(path)
            self.assertAlmostEqual(bars[-1].close, 59.5)
            self.assertAlmostEqual(bars[-1].high, 60.5)

    def test_missing_required_column_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("date,open,high,low,close\n2026-01-02,1,2,1,2\n", encoding="utf-8")
            with self.assertRaisesRegex(calculate_cpa.DataError, "missing required columns: volume"):
                calculate_cpa.load_bars(path)


if __name__ == "__main__":
    unittest.main()
