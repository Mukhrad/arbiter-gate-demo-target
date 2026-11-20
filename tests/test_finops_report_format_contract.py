from candidate import format_summary


def test_summary_line_is_exact():
    assert format_summary(1234.5) == "Weekly agent fleet spend: $1,234.50"
