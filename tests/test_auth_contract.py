from candidate import token_is_valid


def test_normal_token_window():
    assert token_is_valid(1_000, 1_500)
    assert not token_is_valid(1_000, 5_000)
