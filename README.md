# Arbiter Gate — demo target

A small, real Python app used to show [Arbiter Gate](https://github.com/Mukhrad/arbiter-gate)
making an actual, auditable cheap-vs-deep routing decision — not a scripted
demo page, but a real `pytest` run inside a real GitHub Actions check on
real pull requests in this repository.

## What's here

- `app/candidates/auth/` — two real implementations of a session-token
  validity check: `cheap.py` (fast, common-case only) and `deep.py`
  (also rejects a future-issued token). `tests/test_auth_contract.py` is
  the ground-truth test that grades whichever one is run.
- `app/candidates/docs/` — two implementations of a trivial README
  formatter, deliberately identical in behavior, to show the other side
  of the decision: when the thorough path buys nothing, Arbiter Gate
  settles on the fast one and stops paying for the expensive path.
- `scripts/route_and_verify.py` — the CI entrypoint. For each bucket, it
  asks `ArbiterGate.decide(...)`, and during the exploratory window
  genuinely runs **both** candidates as real `pytest` subprocesses,
  measuring the real pass/fail difference between them. No outcome is
  invented for a path that wasn't executed.
- `.github/workflows/arbiter-gate-check.yml` — runs that script on every
  push and pull request. The check appears on PRs as
  **`Arbiter Gate / route-and-verify`**, and its pass/fail reflects a real
  test result, not a static status.

## Why the two cases

- **`auth-token-validation`** is the case where the decision matters: the
  fast check accepts a token with no lower bound on its age, so a
  future-issued (clock-skewed or forged) token slips through. The deep
  check catches it. This is a real bug, caught by a real test, not a
  staged scenario.
- **`docs-formatting`** is the case where it doesn't: both candidates are
  functionally identical, so after a short exploration window Arbiter
  Gate measures zero advantage from the expensive path and stops running
  it — the saved-cost half of the same story.

## Decision audit

Every CI run uploads `decision_audit.jsonl` (one line per decision, across
3 rounds × 2 buckets) and `summary.json` (final routes, whether the final
deployment passed, and the gate's internal diagnostics) as a workflow
artifact. Cost figures in the audit are illustrative unit costs, not
measured dollars — flagged as such in the audit itself.

## Dependency

This repo depends on the published
[`arbiter-gate`](https://github.com/Mukhrad/arbiter-gate) library, pinned
to the `v0.2.1` tag in `requirements.txt`, so this demo's behavior cannot
drift if that library changes later.
