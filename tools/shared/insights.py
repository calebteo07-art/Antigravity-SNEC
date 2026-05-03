#!/usr/bin/env python3
"""Agent 20: Insights Agent — generates a study analytics report per student.

Reads all sheets, identifies weak topics, accuracy trends, and time active.
Produces a readable summary in the terminal.

Usage:
    python tools/shared/insights.py
    python tools/shared/insights.py --student <student_id>
"""

import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

console = Console()


def _parse_float(val, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _parse_int(val, default: int = 0) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def generate_report(student_id: str | None = None) -> None:
    from tools.shared.gsheets import get_rows

    filters = {"student_id": student_id} if student_id else None

    sessions = get_rows("snec_sessions", filters)
    cards = get_rows("snec_flashcards", filters)
    case_results = get_rows("snec_case_results", filters)
    image_results = get_rows("snec_image_results", filters)

    if not any([sessions, cards, case_results, image_results]):
        console.print(Panel(
            "No study data found yet.\n"
            "Complete at least one session, review, or case to see insights.",
            title="Agent 20 - Insights",
            border_style="blue",
        ))
        return

    title = f"Study Report — {student_id[:8]}..." if student_id else "Study Report — All Students"
    console.print(Panel("", title=f"Agent 20 - Insights: {title}", border_style="blue"))

    # Sessions summary
    if sessions:
        topics = [s.get("topic", "") for s in sessions if s.get("topic")]
        total_tokens = sum(_parse_int(s.get("token_count", 0)) for s in sessions)
        console.print(f"\n  [bold]Chatbot Sessions[/bold]")
        console.print(f"    Total sessions  : {len(sessions)}")
        console.print(f"    Total tokens used: {total_tokens:,}")
        console.print(f"    Topics covered  : {', '.join(set(topics[:5]))}" if topics else "")

    # Flash-cards summary
    if cards:
        due_today = 0
        topic_counts: dict[str, int] = defaultdict(int)
        easiness_scores: list[float] = []
        from datetime import date
        today = date.today().isoformat()

        for c in cards:
            topic_counts[c.get("topic_tag", "unknown")] += 1
            ef = _parse_float(c.get("easiness_factor", 2.5))
            easiness_scores.append(ef)
            due = c.get("next_due_date", "")
            if not due or due <= today:
                due_today += 1

        avg_easiness = sum(easiness_scores) / len(easiness_scores) if easiness_scores else 0

        console.print(f"\n  [bold]Flash-cards[/bold]")
        console.print(f"    Total cards     : {len(cards)}")
        console.print(f"    Due today       : {due_today}")
        console.print(f"    Avg easiness    : {avg_easiness:.2f} (2.5=normal, lower=harder)")

        # Weak topics (lowest easiness)
        topic_easiness: dict[str, list[float]] = defaultdict(list)
        for c in cards:
            topic_easiness[c.get("topic_tag", "unknown")].append(
                _parse_float(c.get("easiness_factor", 2.5))
            )

        topic_avg = {t: sum(v) / len(v) for t, v in topic_easiness.items()}
        weak = sorted(topic_avg.items(), key=lambda x: x[1])[:3]

        if weak:
            console.print(f"    Weakest topics  :")
            for topic, ef in weak:
                bar = "█" * max(1, int(ef * 4))
                console.print(f"      {topic:<20} EF={ef:.2f} {bar}")

    # Case results summary
    if case_results:
        scores = [_parse_int(r.get("total_score", 0)) for r in case_results]
        avg_score = sum(scores) / len(scores) if scores else 0
        best = max(scores) if scores else 0
        recent = case_results[-1]

        console.print(f"\n  [bold]Case Simulations[/bold]")
        console.print(f"    Cases attempted : {len(case_results)}")
        console.print(f"    Average score   : {avg_score:.1f}/40 ({avg_score/40*100:.0f}%)")
        console.print(f"    Best score      : {best}/40")

        # Domain breakdown
        domains = [
            ("History", "history_score"),
            ("Investigations", "investigations_score"),
            ("Diagnosis", "diagnosis_score"),
            ("Management", "management_score"),
        ]
        console.print(f"    Domain averages :")
        for label, key in domains:
            vals = [_parse_int(r.get(key, 0)) for r in case_results]
            avg = sum(vals) / len(vals) if vals else 0
            bar = "█" * int(avg)
            console.print(f"      {label:<16} {avg:.1f}/10 {bar}")

    # Image quiz summary
    if image_results:
        scores = [_parse_int(r.get("score", 0)) for r in image_results]
        avg = sum(scores) / len(scores) if scores else 0
        console.print(f"\n  [bold]Image Quizzes[/bold]")
        console.print(f"    Quizzes completed: {len(image_results)}")
        console.print(f"    Average score    : {avg:.1f}/10")

    # Study recommendation
    console.print(f"\n  [bold]Recommendations[/bold]")
    if cards and due_today > 0:
        console.print(f"    - {due_today} flash-card(s) due — run review_session.py")
    if not case_results:
        console.print(f"    - Try your first clinical case — run cases/run_case.py")
    if case_results and avg_score < 28:
        weakest_domain = min(
            [("History", "history_score"), ("Investigations", "investigations_score"),
             ("Diagnosis", "diagnosis_score"), ("Management", "management_score")],
            key=lambda x: sum(_parse_int(r.get(x[1], 0)) for r in case_results)
        )
        console.print(f"    - Focus on {weakest_domain[0]} — lowest scoring domain in cases")
    console.print()


def main() -> None:
    student_id = None
    if "--student" in sys.argv:
        idx = sys.argv.index("--student")
        if idx + 1 < len(sys.argv):
            student_id = sys.argv[idx + 1]

    generate_report(student_id)


if __name__ == "__main__":
    main()
