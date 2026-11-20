"""Fast formatter for the weekly cost-summary line."""


def format_summary(total: float) -> str:
    return f"Weekly agent fleet spend: ${total:,.2f}"
