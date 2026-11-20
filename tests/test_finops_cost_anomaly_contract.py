from candidate import is_cost_anomalous

# 12 "normal" hours for this fleet: noisy but centered around $11-12/hr.
NORMAL = [10, 12, 11, 13, 10, 14, 12, 11, 13, 10, 12, 11]

# A stuck retry loop: sustained ~3x the fleet's own baseline for half a
# day, but every single hour stays comfortably under a $50 hard cap.
LEAK = [34, 33, 35, 32, 36, 33, 34, 32, 35, 33, 34, 32]


def test_normal_fleet_spend_is_not_flagged():
    assert not is_cost_anomalous(NORMAL + NORMAL)


def test_sustained_leak_under_hard_cap_is_flagged():
    assert is_cost_anomalous(NORMAL + LEAK)


def test_spike_over_hard_cap_is_flagged():
    assert is_cost_anomalous(NORMAL + [55])
