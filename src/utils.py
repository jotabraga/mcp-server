from src.const import MAX_RESPONSE_LENGTH


def truncate_response(text: str, max_length: int = MAX_RESPONSE_LENGTH) -> str:
    """Trim an oversized response and append a visible warning.

    The warning itself must fit inside the budget, so we reserve its length before slicing.
    """
    if len(text) <= max_length:
        return text

    warning = (
        f" ... [WARNING: Response truncated by the MCP server due to the {max_length} "
        "character limit. Only partial data was delivered; the missing data was not received.]"
    )
    # Guard the edge case where the budget is smaller than the warning itself.
    keep = max(max_length - len(warning), 0)
    return text[:keep] + warning
