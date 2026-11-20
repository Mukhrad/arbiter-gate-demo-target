"""Render the decision audit as Markdown for GitHub's Step Summary.

This exists because GitHub requires a signed-in session to download a
workflow *artifact*, even on a public repo -- so anyone without a GitHub
account (or who just doesn't want to log in) cannot otherwise see the
actual evidence behind a passing check. The run's own log page, and the
Step Summary rendered on it, are visible to anyone with the URL, no
sign-in required. This script makes the real evidence -- including a
genuine pytest failure, not a paraphrase of one -- show up there.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    summary = json.loads((args.output_dir / "summary.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in (args.output_dir / "decision_audit.jsonl").read_text(encoding="utf-8").splitlines()]

    print(f"## Arbiter Gate decision audit\n")
    print(f"**Verdict:** `{summary['verdict']}`  ")
    print(f"**Final routes:** " + ", ".join(f"`{b}` -> `{p}`" for b, p in summary["final_routes"].items()) + "\n")

    for bucket in summary["final_routes"]:
        bucket_rows = [r for r in rows if r["bucket"] == bucket]
        print(f"### {bucket} — {bucket_rows[0]['title']}\n")
        print("| round | reason | deployed | deployed passed | shadow | shadow passed | measured advantage |")
        print("|---|---|---|---|---|---|---|")
        for r in bucket_rows:
            shadow = r["shadow"] or {}
            print(
                f"| {r['round']} | {r['decision']['reason']} | {r['deployed']['candidate']} "
                f"| {r['deployed']['passed']} | {shadow.get('candidate', '—')} "
                f"| {shadow.get('passed', '—')} | {r['measured_advantage_deep_minus_cheap']} |"
            )
        print()
        failing = next((r for r in bucket_rows if r["shadow"] and not r["shadow"]["passed"]), None)
        if failing:
            print("<details><summary>Real pytest output of the path that failed (not paraphrased)</summary>\n")
            print("```")
            print(failing["shadow"]["test_output"])
            print("```\n</details>\n")

    print(
        "Full machine-readable log: `decision_audit.jsonl` / `summary.json`, "
        "also uploaded as a workflow artifact (requires a GitHub sign-in to download) "
        "and committed to `proof/latest/` on every push to `main` (no sign-in needed)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
