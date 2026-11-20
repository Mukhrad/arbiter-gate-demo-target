"""Thorough session-token check: also rejects a token issued in the future,
which the fast check above accepts by omission."""


def token_is_valid(issued_at: int, now: int, ttl_seconds: int = 3600) -> bool:
    age = now - issued_at
    return 0 <= age <= ttl_seconds
