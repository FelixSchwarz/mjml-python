import re


__all__ = ['makeLowerBreakpoint']

def makeLowerBreakpoint(breakpoint: str) -> str:
    """
    Converts a breakpoint like '480px' to '479px' by subtracting 1 from the pixel value.
    This is used for max-width media queries to avoid overlap with min-width queries.

    Args:
        breakpoint: A string like '480px'

    Returns:
        A string like '479px', or the original breakpoint if parsing fails
    """
    try:
        match = re.search(r'[0-9]+', breakpoint)
        if match:
            pixels = int(match.group(0))
            return f'{pixels - 1}px'
        return breakpoint
    except Exception:
        return breakpoint
