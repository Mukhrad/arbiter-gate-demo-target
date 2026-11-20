"""Fast, narrow session-token check: validates the common case only."""


def token_is_valid(issued_at: int, now: int, ttl_seconds: int = 3600) -> bool:
    return now - issued_at <= ttl_seconds
