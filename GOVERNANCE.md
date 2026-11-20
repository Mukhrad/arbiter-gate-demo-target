# Governance: how this platform is built and tested

This repo is the test platform for Arbiter Gate's go-to-market, not a
one-off demo. It follows one standing rule carried over from the parent
project: **the author of a change never reviews it themselves.** Every
claim of readiness here is checked by a party that did not build it.

## Roles

- **Engineer (Claude):** builds and extends the platform -- new
  verticals, new cases, new infrastructure -- always with a genuine,
  independently-verified cheap/deep differential behind every case that
  claims one (never a scripted result; see `scripts/route_and_verify.py`
  and each case's own `tests/test_*_contract.py`). Reports limitations
  plainly, including ones that make the platform look less finished
  (see README's "Known limitations").
- **Client ("نواة العميل" -- the Client Nucleus):** ChatGPT, or another
  model not involved in building this platform, playing a specific,
  skeptical persona (a real engineer or FinOps lead who would actually
  use this) and evaluating the platform as it stands, not as it is
  described. The Client Nucleus is the single point of contact between
  the engineering side and that outside judgment -- every evaluation
  request and every verdict passes through it, logged in this repo's PR
  history, never only in chat.

## Protocol

1. A new vertical or case is proposed, built, and verified locally
   (real pytest, real differential, no scripted pass/fail) before any
   PR is opened.
2. It ships as a real, reviewable pull request -- never a direct commit
   to `main` -- with the Arbiter Gate check running on it.
3. Once merged, a Client Nucleus evaluation request is sent: the real
   PR links, the real Actions run, and an explicit instruction to
   verify independently rather than trust the message. See
   `docs/client-nucleus-prompt-template.md` for the live template.
4. Every verdict -- including a negative or skeptical one -- is logged
   back into this repo's history (a GOVERNANCE.md update, a README
   section, or a follow-up PR that fixes what the verdict found). A
   verdict is never quietly dropped if it's unfavorable.
5. Readiness for a real client launch is judged by the accumulated
   record of Client Nucleus verdicts across verticals and cases, not by
   the Engineer's own assessment of the work.

## Verticals under test

| Vertical | Buckets | Status |
|---|---|---|
| DevOps / coding agents | `auth-token-validation`, `docs-formatting`, `devops-migration-sql` | Live, Client-Nucleus-reviewed (see PR #1, #2) |
| FinOps / agent fleet cost governance | `finops-cost-anomaly`, `finops-report-formatting` | Live, built to the same standard, pending Client Nucleus review |

Each bucket pairs a genuine safety- or cost-relevant case with a
genuine "cheap already suffices" counter-case, so neither vertical's
story is just "always escalate."
