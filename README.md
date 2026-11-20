# Arbiter Gate — demo target

[![Arbiter Gate](https://github.com/Mukhrad/arbiter-gate-demo-target/actions/workflows/arbiter-gate-check.yml/badge.svg)](https://github.com/Mukhrad/arbiter-gate-demo-target/actions/workflows/arbiter-gate-check.yml)

A real, growing test platform for [Arbiter Gate](https://github.com/Mukhrad/arbiter-gate)
across multiple verticals -- not a scripted demo page, but a real
`pytest` run inside a real GitHub Actions check on real pull requests in
this repository. See [GOVERNANCE.md](GOVERNANCE.md) for how this
platform is built, tested, and independently reviewed (the "Client
Nucleus" protocol).

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

## Verticals and buckets

Each vertical pairs a genuine safety- or cost-relevant case with a
genuine "cheap already suffices" counter-case:

**DevOps / coding agents**
- **`auth-token-validation`** — the fast check accepts a token with no
  lower bound on its age, so a future-issued (clock-skewed or forged)
  token slips through; the deep check catches it. A real bug, caught by
  a real test.
- **`devops-migration-sql`** — the fast candidate emits a plain
  `CREATE INDEX`, which takes a table-locking write lock for the
  duration of the build; the deep candidate emits `CREATE INDEX
  CONCURRENTLY`. On a real production table this is the difference
  between a no-op and an outage.
- **`docs-formatting`** — both candidates are functionally identical, so
  after a short exploration window Arbiter Gate measures zero advantage
  from the expensive path and stops running it.

**FinOps / agent fleet cost governance**
- **`finops-cost-anomaly`** — the fast check only watches a fixed
  hard-cap dollar threshold per hour; it misses a stuck agent retry loop
  that sustains ~3x the fleet's own baseline spend for half a day
  without ever crossing the cap. The deep check compares against the
  fleet's recent baseline and catches it.
- **`finops-report-formatting`** — both candidates produce an identical
  summary string; the expensive path buys nothing and Arbiter Gate stops
  paying for it.

## Decision audit

Every CI run uploads `decision_audit.jsonl` and `summary.json` (final routes, whether the final
deployment passed, and the gate's internal diagnostics) as a workflow
artifact (one line per decision, across 3 rounds × 5 buckets). Cost
figures in the audit are illustrative unit costs, not measured dollars
— flagged as such in the audit itself.

**You do not need a GitHub account to see this evidence.** Downloading a
workflow artifact requires a GitHub sign-in, which is a real barrier for
an outside reviewer, so the same evidence is also published two other
ways that need no sign-in at all:

- Every run's own [Summary page](https://github.com/Mukhrad/arbiter-gate-demo-target/actions/workflows/arbiter-gate-check.yml)
  renders the decision table and, for the `auth-token-validation`
  bucket, the real (unedited) `pytest` failure output of the fast
  candidate -- see `scripts/render_summary.py`.
- [`proof/latest/`](proof/latest) in this repo is overwritten by CI on
  every push to `main` with that run's own `decision_audit.jsonl` and
  `summary.json` -- an ordinary file in the repo, browsable like any
  other.

Each run's `summary.json` also reports `persistent_state`: whether this
run loaded learned evidence from
[`.arbiter_state/gate_state.json`](.arbiter_state) (another ordinary,
no-sign-in-needed repo file) or started genuinely fresh. When it loaded
prior state, decisions in round 1 of that run may already read
`"trusted"` or `"blocked"` instead of `"exploring"` -- that is the
mechanism actually carrying evidence across separate CI runs, not a
reset each time. See "Known limitations" below for exactly what this
does and does not prove.

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

## Known limitations

- **The gate now persists settled evidence across separate CI runs**
  (`.arbiter_state/gate_state.json`, committed by the same
  `publish-latest-proof` job that already commits `proof/latest/` --
  the PR-facing check itself stays `contents: read`; only that one job,
  running solely on pushes to `main`, has `contents: write`). This
  closes the specific gap an independent reviewer raised (every CI run
  re-exploring from zero): verified locally, two consecutive runs
  sharing the same state file show the second run's very first decision
  on each bucket already `"trusted"` or `"blocked"`, not `"exploring"`.
  **What this does not yet show**: that the resulting routing is
  actually cheaper or better than a fixed baseline over many real,
  independent decisions -- only that evidence correctly survives a
  process boundary. A real continuing-benefit claim needs a shadow
  comparison against a fixed baseline on cases this repo did not design
  around (tracked as the next step in
  [GOVERNANCE.md](GOVERNANCE.md) / `customer_nucleus/`), not more
  buckets inside this repo.
- **Costs are illustrative unit costs**, not measured dollars or latency
  from a real model call -- flagged as such in the audit itself.
- **A handful of hand-picked buckets, not a general classifier.** This
  repo shows the mechanism on specific, verified cases across two
  verticals, not an automatic way to decide which bucket a new kind of
  change belongs to; that classification is still the integrator's job.

## Live proof

Every pull request below is this repo's own evidence, kept open for
review rather than squashed away, and every verdict on them is logged
under the "Client Nucleus" protocol in [GOVERNANCE.md](GOVERNANCE.md):

- [PR #1 — Harden deep token check against future-issued tokens](https://github.com/Mukhrad/arbiter-gate-demo-target/pull/1)
  — security-sensitive. The CI run genuinely executed the fast
  candidate, watched it fail `test_future_issued_token_is_rejected`,
  and escalated to the thorough one.
- [PR #2 — Docs: point reviewers at the decision audit, not just the check mark](https://github.com/Mukhrad/arbiter-gate-demo-target/pull/2)
  — documentation-only, the deliberate "cheap suffices" contrast.
- PR #5 — adds `devops-migration-sql` (lock-safety) and the full FinOps
  vertical (`finops-cost-anomaly`, `finops-report-formatting`), extending
  the same escalate-when-real / stay-cheap-when-not story across a
  second product vertical.

Escalate when the evidence says to, stay cheap when it doesn't -- and
every one of these calls is visible as a real, named GitHub check
(`Arbiter Gate / route-and-verify`), not a page that only describes what
the gate would do.

## Dependency

This repo depends on the published
[`arbiter-gate`](https://github.com/Mukhrad/arbiter-gate) library, pinned
to the `v0.2.1` tag in `requirements.txt`, so this demo's behavior cannot
drift if that library changes later.
