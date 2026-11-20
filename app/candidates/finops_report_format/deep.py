"""Thorough formatter for the weekly cost-summary line -- functionally
identical to the fast one. Nothing about this string needs the extra
scrutiny."""


def format_summary(total: float) -> str:
    return f"Weekly agent fleet spend: ${total:,.2f}"
