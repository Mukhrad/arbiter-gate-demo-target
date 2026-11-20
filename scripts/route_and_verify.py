"""Arbiter Gate CI check for this repo.

For each named case below, this script asks the published Arbiter Gate
library whether a given decision bucket should route to the fast or the
thorough check. During each bucket's exploratory window BOTH checks are
genuinely executed as real pytest subprocesses against the real candidate
code in app/candidates/<case>/{cheap,deep}.py, graded by the real contract
test in tests/. No score is invented for a path that was not run.

This mirrors examples/devops_live_proof/run_proof.py in the Arbiter Gate
library itself, but runs as this repo's own GitHub Actions check, against
this repo's own code, on every push and pull request.

Exit code reflects whether the path Arbiter Gate actually deployed in the
final round passed its real tests -- that is what the GitHub Check status
is reporting, not a static always-green stub.

Starting with this script's v0.3.0-dependent revision, the gate's learned
state (not any open/unreported decision, only settled evidence) is loaded
from and saved back to .arbiter_state/gate_state.json, stamped with this
repo's REPO_ID. On the very first run ever, no such file exists yet and the
gate starts genuinely fresh -- every subsequent run picks up exactly where
the last one left off, so a bucket that was already "trusted" or "blocked"
in a prior run does not re-explore from zero. The file is committed back to
the repo by the same publish-latest-proof CI job that already commits
proof/latest/*, so it carries forward across GitHub Actions runs, which
otherwise share no disk between them.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from arbiter_gate.adapters.shadow import ShadowExecutionAdapter
from arbiter_gate.core.gate import ArbiterGate, ArbiterGateConfig
from arbiter_gate.core.value_estimator import ValueEstimatorConfig
from arbiter_gate.integrations import load_state_or_new, save_state_atomic

ROOT = Path(__file__).resolve().parent.parent
REPO_ID = "Mukhrad/arbiter-gate-demo-target"
DEFAULT_STATE_PATH = ROOT / ".arbiter_state" / "gate_state.json"

# (bucket, candidates_dir, contract_test_file, human title)
CASES = (
    (
        "auth-token-validation",
        ROOT / "app" / "candidates" / "auth",
        ROOT / "tests" / "test_auth_contract.py",
        "Session-token validity check (security-sensitive)",
    ),
    (
        "docs-formatting",
        ROOT / "app" / "candidates" / "docs",
        ROOT / "tests" / "test_docs_contract.py",
        "README install-snippet formatter (no safety stakes)",
    ),
    (
        "devops-migration-sql",
        ROOT / "app" / "candidates" / "devops_migration",
        ROOT / "tests" / "test_devops_migration_contract.py",
        "Production index migration (lock-safety-sensitive)",
    ),
    (
        "finops-cost-anomaly",
        ROOT / "app" / "candidates" / "finops_cost_anomaly",
        ROOT / "tests" / "test_finops_cost_anomaly_contract.py",
        "Agent fleet cost-leak detection (budget-safety-sensitive)",
    ),
    (
        "finops-report-formatting",
        ROOT / "app" / "candidates" / "finops_report_format",
        ROOT / "tests" / "test_finops_report_format_contract.py",
        "Weekly cost-summary formatter (no safety stakes)",
    ),
)


def run_candidate(candidates_dir: Path, contract_test: Path, candidate_name: str) -> tuple[dict, float]:
    with tempfile.TemporaryDirectory(prefix="arbiter-demo-") as tmp:
        work = Path(tmp)
        shutil.copy2(candidates_dir / f"{candidate_name}.py", work / "candidate.py")
        shutil.copy2(contract_test, work / "test_candidate.py")
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "test_candidate.py"],
            cwd=work,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    passed = completed.returncode == 0
    payload = {
        "candidate": candidate_name,
        "passed": passed,
        "exit_code": completed.returncode,
        "test_output": completed.stdout.strip()[-2000:],
    }
    return payload, 1.0 if passed else 0.0


def run_all(output_dir: Path, rounds: int = 3, state_path: Path = DEFAULT_STATE_PATH) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / "decision_audit.jsonl"
    config = ArbiterGateConfig(
        exploratory_decisions=2,
        value_config=ValueEstimatorConfig(
            uncertainty_penalty=0.0,
            min_samples_for_lcb=2,
            value_margin=0.0,
        ),
    )
    gate, state_load_report = load_state_or_new(state_path, REPO_ID, config)
    audit: list[dict] = []

    for round_index in range(1, rounds + 1):
        for bucket, candidates_dir, contract_test, title in CASES:
            adapter = ShadowExecutionAdapter(
                gate=gate,
                cheap_fn=lambda d=candidates_dir, t=contract_test: run_candidate(d, t, "cheap"),
                expensive_fn=lambda d=candidates_dir, t=contract_test: run_candidate(d, t, "deep"),
                cheap_cost=1.0,
                expensive_cost=5.0,
            )
            result = adapter.decide_and_run(bucket)
            if result.immediate_advantage is not None:
                adapter.report_delayed(result.decision, result.immediate_advantage)

            row = {
                "round": round_index,
                "bucket": bucket,
                "title": title,
                "decision": {
                    "selected_path": "deep" if result.decision.use_expensive else "cheap",
                    "reason": result.decision.reason,
                },
                "deployed": result.deployed_payload,
                "shadow": result.shadow_payload,
                "measured_advantage_deep_minus_cheap": result.immediate_advantage,
                "deployed_cost_units": result.deployed_cost,
                "shadow_cost_units": result.shadow_cost,
                "cost_units_are_illustrative": True,
            }
            audit.append(row)

    audit_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in audit),
        encoding="utf-8",
    )
    save_state_atomic(gate, state_path, REPO_ID)
    final_round = [row for row in audit if row["round"] == rounds]
    summary = {
        "verdict": "ROUTE_AND_VERIFY_PASSED"
        if all(row["deployed"]["passed"] for row in final_round)
        else "ROUTE_AND_VERIFY_FAILED",
        "rounds": rounds,
        "decisions": len(audit),
        "final_routes": {row["bucket"]: row["decision"]["selected_path"] for row in final_round},
        "all_final_deployments_passed": all(row["deployed"]["passed"] for row in final_round),
        "gate_diagnostics": gate.diagnostics(),
        "audit_log": audit_path.name,
        "persistent_state": {
            "repo_id": REPO_ID,
            "state_file": str(state_path),
            "loaded_from_prior_run": state_load_report["loaded"],
            "load_detail": state_load_report["reason"],
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--state-path", type=Path, default=DEFAULT_STATE_PATH)
    args = parser.parse_args()
    summary = run_all(args.output, args.rounds, args.state_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["verdict"] == "ROUTE_AND_VERIFY_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
