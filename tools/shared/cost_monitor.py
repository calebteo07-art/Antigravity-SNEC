#!/usr/bin/env python3
"""Agent 19: Cost Monitor — tracks Claude API usage and projects monthly spend.

Reads snec_api_usage sheet, computes weekly totals, and flags if spend
exceeds the configured threshold.

Usage:
    python tools/shared/cost_monitor.py
    python tools/shared/cost_monitor.py --threshold 10.00
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

console = Console()

# Claude Sonnet 4.6 pricing (USD per million tokens) — update if pricing changes
INPUT_PRICE_PER_M = 3.00
OUTPUT_PRICE_PER_M = 15.00
CACHE_PRICE_PER_M = 0.30

DEFAULT_THRESHOLD_USD = 20.00


def _compute_cost(input_tokens: int, output_tokens: int, cached_tokens: int) -> float:
    return (
        (input_tokens / 1_000_000) * INPUT_PRICE_PER_M
        + (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_M
        + (cached_tokens / 1_000_000) * CACHE_PRICE_PER_M
    )


def _parse_int(val) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def _parse_float(val) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def analyse_usage(threshold_usd: float = DEFAULT_THRESHOLD_USD) -> None:
    from tools.shared.gsheets import get_rows

    rows = get_rows("snec_api_usage")

    if not rows:
        console.print(Panel(
            "No API usage recorded yet.\n"
            "Usage is logged automatically when ANTHROPIC_API_KEY is set and features are used.",
            title="Agent 19 - Cost Monitor",
            border_style="blue",
        ))
        return

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Parse and bucket rows
    all_rows = []
    for r in rows:
        try:
            ts = datetime.fromisoformat(r.get("timestamp", "").replace("Z", "+00:00"))
        except ValueError:
            continue
        all_rows.append({
            "ts": ts,
            "feature": r.get("feature", "unknown"),
            "model": r.get("model", ""),
            "input": _parse_int(r.get("input_tokens", 0)),
            "output": _parse_int(r.get("output_tokens", 0)),
            "cached": _parse_int(r.get("cached_tokens", 0)),
            "cost": _parse_float(r.get("estimated_cost_usd", 0)),
        })

    week_rows = [r for r in all_rows if r["ts"] >= week_ago]
    month_rows = [r for r in all_rows if r["ts"] >= month_ago]

    def totals(bucket):
        return {
            "calls": len(bucket),
            "input": sum(r["input"] for r in bucket),
            "output": sum(r["output"] for r in bucket),
            "cached": sum(r["cached"] for r in bucket),
            "cost": sum(r["cost"] for r in bucket),
        }

    w = totals(week_rows)
    m = totals(month_rows)
    a = totals(all_rows)

    # Projection
    if w["calls"] > 0:
        daily_rate = w["cost"] / 7
        projected_monthly = daily_rate * 30
    else:
        projected_monthly = 0.0

    # Summary table
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    table.add_column("Period", min_width=12)
    table.add_column("API Calls", justify="right")
    table.add_column("Input Tokens", justify="right")
    table.add_column("Output Tokens", justify="right")
    table.add_column("Cached Tokens", justify="right")
    table.add_column("Cost (USD)", justify="right")

    table.add_row("This week", str(w["calls"]), f"{w['input']:,}", f"{w['output']:,}",
                  f"{w['cached']:,}", f"${w['cost']:.4f}")
    table.add_row("Last 30 days", str(m["calls"]), f"{m['input']:,}", f"{m['output']:,}",
                  f"{m['cached']:,}", f"${m['cost']:.4f}")
    table.add_row("All time", str(a["calls"]), f"{a['input']:,}", f"{a['output']:,}",
                  f"{a['cached']:,}", f"${a['cost']:.4f}")

    console.print(Panel(table, title="Agent 19 - Cost Monitor", border_style="blue"))

    # Projection and threshold
    proj_color = "red" if projected_monthly > threshold_usd else "green"
    console.print(
        f"  Projected monthly spend : [{proj_color}]${projected_monthly:.2f}[/{proj_color}]  "
        f"(threshold: ${threshold_usd:.2f})"
    )

    if projected_monthly > threshold_usd:
        console.print(
            f"\n  [bold red]WARNING:[/bold red] Projected spend exceeds threshold. "
            f"Review usage or increase threshold with --threshold."
        )

    # Feature breakdown for this week
    if week_rows:
        feature_totals: dict[str, float] = {}
        for r in week_rows:
            feature_totals[r["feature"]] = feature_totals.get(r["feature"], 0) + r["cost"]

        console.print("\n  Weekly cost by feature:")
        for feat, cost in sorted(feature_totals.items(), key=lambda x: -x[1]):
            console.print(f"    {feat:<20} ${cost:.4f}")

    console.print()


def main() -> None:
    threshold = DEFAULT_THRESHOLD_USD
    if "--threshold" in sys.argv:
        idx = sys.argv.index("--threshold")
        if idx + 1 < len(sys.argv):
            try:
                threshold = float(sys.argv[idx + 1])
            except ValueError:
                pass

    analyse_usage(threshold)


if __name__ == "__main__":
    main()
