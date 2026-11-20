# Arbiter Gate — demo target

[![Arbiter Gate](https://github.com/Mukhrad/arbiter-gate-demo-target/actions/workflows/arbiter-gate-check.yml/badge.svg)](https://github.com/Mukhrad/arbiter-gate-demo-target/actions/workflows/arbiter-gate-check.yml)

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

## What a reviewer should look for

Open the "Arbiter Gate / route-and-verify" check on any pull request in
this repo (including this one, which touches no application code). Its
uploaded `summary.json` names, per bucket, which path was actually
deployed in the final round and whether that deployment's own tests
passed -- and for `docs-formatting` specifically, that the thorough path
was tried, measured, and then stopped because it never beat the fast
one. That stopping is the saved-cost half of the story; the
`auth-token-validation` bucket (see the `fix/auth-token-expiry-window`
history) is the half where stopping early would have been the wrong
call, and the audit shows a real test failure proving it.

## Live proof

Two merged pull requests are this repo's own evidence, kept open for
review rather than squashed away:

- [PR #1 — Harden deep token check against future-issued tokens](https://github.com/Mukhrad/arbiter-gate-demo-target/pull/1)
  — the security-sensitive case. The regression test and the fix land
  in the same change; the CI run on that PR genuinely executed the fast
  candidate, watched it fail `test_future_issued_token_is_rejected`,
  and escalated to the thorough one -- all recorded in that run's
  `decision_audit.jsonl`.
- [PR #2 — Docs: point reviewers at the decision audit, not just the check mark](https://github.com/Mukhrad/arbiter-gate-demo-target/pull/2)
  — a documentation-only change, included as the deliberate contrast:
  Arbiter Gate still ran, still measured both candidates for the
  `docs-formatting` bucket, and settled on the fast one because the
  thorough path never beat it. No code to fix, so no reason to pay for
  the expensive path.

Together they are the full pitch in two PRs: escalate when the evidence
says to, stay cheap when it doesn't -- and both calls are visible as a
real, named GitHub check (`Arbiter Gate / route-and-verify`), not a
page that only describes what the gate would do.

## Dependency

This repo depends on the published
[`arbiter-gate`](https://github.com/Mukhrad/arbiter-gate) library, pinned
to the `v0.2.1` tag in `requirements.txt`, so this demo's behavior cannot
drift if that library changes later.
