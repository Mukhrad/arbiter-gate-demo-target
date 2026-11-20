from candidate import token_is_valid


def test_normal_token_window():
    assert token_is_valid(1_000, 1_500)
    assert not token_is_valid(1_000, 5_000)


def test_future_issued_token_is_rejected():
    # A token whose issued_at is after "now" is either clock-skewed or
    # forged. The fast check has no lower bound and accepts it; this is
    # the real bug the deep check exists to catch.
    assert not token_is_valid(2_000, 1_000)
