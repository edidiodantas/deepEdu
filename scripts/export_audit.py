#!/usr/bin/env python3
"""Exporta logs de auditoria e consentimento para CSV (RF47 / AU-05)."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.audit import init_audit  # noqa: E402
from app.audit.repository import fetch_audit_logs, fetch_consent_logs  # noqa: E402


def export_csv(
    output: Path,
    date_from: str | None,
    date_to: str | None,
    include_consent: bool,
) -> None:
    audit_rows = fetch_audit_logs(date_from=date_from, date_to=date_to)
    consent_rows = fetch_consent_logs(date_from=date_from, date_to=date_to) if include_consent else []

    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "event_id",
                "timestamp",
                "correlation_id",
                "actor_type",
                "actor_id",
                "session_id",
                "action",
                "resource",
                "outcome",
                "metadata",
                "langsmith_run_id",
            ]
        )
        for row in audit_rows:
            writer.writerow(
                [
                    row["event_id"],
                    row["timestamp"],
                    row["correlation_id"],
                    row["actor_type"],
                    row["actor_id"],
                    row["session_id"],
                    row["action"],
                    row["resource"],
                    row["outcome"],
                    str(row["metadata"]),
                    row.get("langsmith_run_id") or "",
                ]
            )
        if include_consent:
            writer.writerow([])
            writer.writerow(["phone_hash", "status", "terms_version", "created_at"])
            for row in consent_rows:
                writer.writerow([row["phone_hash"], row["status"], row["terms_version"], row["created_at"]])

    print(f"Exportado: {output} ({len(audit_rows)} eventos, {len(consent_rows)} consentimentos)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Exportar auditoria deepEdu")
    parser.add_argument("--from", dest="date_from", default=None, help="Data inicial ISO")
    parser.add_argument("--to", dest="date_to", default=None, help="Data final ISO")
    parser.add_argument("--output", default="reports/audit_export.csv", help="Arquivo CSV de saida")
    parser.add_argument("--no-consent", action="store_true", help="Nao incluir consent_log")
    args = parser.parse_args()

    init_audit()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    export_csv(output, args.date_from, args.date_to, include_consent=not args.no_consent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
