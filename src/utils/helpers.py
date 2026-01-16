"""
Helper Utilities

General-purpose helper functions used across the application.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import hashlib
import secrets
import string


def generate_random_string(length: int = 32) -> str:
    """
    Generate a cryptographically secure random string.

    Args:
        length: The length of the string to generate.

    Returns:
        A random string of the specified length.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_token() -> str:
    """
    Generate a secure token for API keys or verification links.

    Returns:
        A 64-character hexadecimal token.
    """
    return secrets.token_hex(32)


def hash_string(value: str) -> str:
    """
    Create a SHA-256 hash of a string.

    Args:
        value: The string to hash.

    Returns:
        The hexadecimal hash digest.
    """
    return hashlib.sha256(value.encode()).hexdigest()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string.

    Args:
        dt: The datetime to format.
        format_str: The format string.

    Returns:
        Formatted datetime string.
    """
    return dt.strftime(format_str)


def parse_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse a datetime string.

    Args:
        date_string: The string to parse.
        format_str: The expected format.

    Returns:
        Parsed datetime object.
    """
    return datetime.strptime(date_string, format_str)


def time_ago(dt: datetime) -> str:
    """
    Get a human-readable time difference from now.

    Args:
        dt: The datetime to compare.

    Returns:
        Human-readable string like "2 hours ago".
    """
    now = datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"


def paginate(
    items: List[Any],
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """
    Paginate a list of items.

    Args:
        items: The list to paginate.
        page: Current page number (1-indexed).
        per_page: Items per page.

    Returns:
        Dictionary with pagination metadata and items.
    """
    total = len(items)
    total_pages = (total + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page

    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def merge_dicts(base: Dict, updates: Dict) -> Dict:
    """
    Deep merge two dictionaries.

    Args:
        base: The base dictionary.
        updates: Dictionary with updates to apply.

    Returns:
        Merged dictionary.
    """
    result = base.copy()

    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: The list to split.
        chunk_size: Maximum items per chunk.

    Returns:
        List of chunks.
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
