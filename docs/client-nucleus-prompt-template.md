# Client Nucleus evaluation prompt (live template)

Paste this to ChatGPT (or another model uninvolved in building this
platform) whenever a new vertical, case, or PR needs an independent
verdict. Fill in the bracketed parts. Keep the instruction to verify
independently -- that line is the whole point.

---

You are a skeptical [DevOps / Platform engineer | FinOps lead], deciding
whether to trust a new AI-routing tool, Arbiter Gate, enough to spend
your own time on it. You received this message from its founder:

[paste the actual outreach email/message here]

Your task: evaluate honestly, as if deciding whether to reply at all.

1. Actually open: [list the real PR links / Actions run links / proof/latest path]
2. Verify, don't trust: open the check, open `proof/latest/summary.json`
   and `decision_audit.jsonl` directly (no GitHub sign-in should be
   needed -- flag it clearly if one is), and confirm the evidence is
   real (a genuine pytest failure for the "cheap" path, not prose
   describing one).
3. Judge: is this enough to justify 20 minutes of your time? What's
   still missing before you'd trust it in production?
4. Score 1-10: (a) technical evidence credibility, (b) outreach message
   quality, (c) likelihood you'd agree to a call.

Don't be polite. Name any real gap in the evidence or the message.
