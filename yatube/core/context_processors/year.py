"""Module with context processor of year variable."""

import datetime as dt


def year(request) -> dict:
    """Add current year variable.
    
    Args:
        request: current request to add variable.
    
    Returns:
        current year variable.
    """
    return {
        'year': dt.date.today().year
    }
