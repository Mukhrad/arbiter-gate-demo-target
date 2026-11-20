"""Thorough session-token check. As of this commit it still shares the
fast check's logic -- see PR "fix/auth-token-expiry-window" for the real
difference Arbiter Gate later detects and routes around."""


def token_is_valid(issued_at: int, now: int, ttl_seconds: int = 3600) -> bool:
    return now - issued_at <= ttl_seconds
