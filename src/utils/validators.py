"""
Validation Utilities

Common validation functions used across the application.
"""
import re
from datetime import datetime, date
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email: The email address to validate.

    Returns:
        True if valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> dict:
    """
    Check password strength and return validation results.

    Args:
        password: The password to validate.

    Returns:
        Dictionary with 'valid' boolean and list of 'errors'.
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "strength": _calculate_password_strength(password, errors)
    }


def _calculate_password_strength(password: str, errors: list) -> str:
    """Calculate password strength based on criteria met."""
    score = 5 - len(errors)

    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1

    if score >= 6:
        return "strong"
    elif score >= 4:
        return "medium"
    else:
        return "weak"


def validate_username(username: str) -> dict:
    """
    Validate username format.

    Args:
        username: The username to validate.

    Returns:
        Dictionary with 'valid' boolean and list of 'errors'.
    """
    errors = []

    if len(username) < 3:
        errors.append("Username must be at least 3 characters long")

    if len(username) > 30:
        errors.append("Username cannot exceed 30 characters")

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        errors.append(
            "Username must start with a letter and contain only "
            "letters, numbers, underscores, and hyphens"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_date_range(
    start_date: Optional[date],
    end_date: Optional[date]
) -> dict:
    """
    Validate a date range.

    Args:
        start_date: The start date.
        end_date: The end date.

    Returns:
        Dictionary with 'valid' boolean and optional 'error' message.
    """
    if start_date and end_date and start_date > end_date:
        return {
            "valid": False,
            "error": "Start date must be before or equal to end date"
        }

    return {"valid": True}


def sanitize_string(value: str) -> str:
    """
    Sanitize a string by removing potentially dangerous characters.

    Args:
        value: The string to sanitize.

    Returns:
        Sanitized string.
    """
    # Remove null bytes
    value = value.replace('\x00', '')

    # Strip leading/trailing whitespace
    value = value.strip()

    # Remove control characters except newlines and tabs
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)

    return value
