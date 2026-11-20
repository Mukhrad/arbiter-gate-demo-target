"""Thorough cost check: also flags sustained spend well above the fleet's
own recent baseline, even when every single hour stays under the hard cap
-- the pattern a stuck agent retry loop actually produces."""


def is_cost_anomalous(hourly_spend: list, cap: float = 50.0) -> bool:
    if any(h > cap for h in hourly_spend):
        return True
    if len(hourly_spend) < 12:
        return False
    half = len(hourly_spend) // 2
    baseline_window = sorted(hourly_spend[:half])
    recent_window = sorted(hourly_spend[half:])
    baseline = baseline_window[len(baseline_window) // 2]
    recent = recent_window[len(recent_window) // 2]
    return recent > 2.0 * baseline
