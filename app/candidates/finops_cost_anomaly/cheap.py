"""Fast cost check: a single fixed hard-cap threshold per hour."""


def is_cost_anomalous(hourly_spend: list, cap: float = 50.0) -> bool:
    return any(h > cap for h in hourly_spend)
