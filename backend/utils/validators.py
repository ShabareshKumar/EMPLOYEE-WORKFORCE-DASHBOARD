"""
Input validation utilities
Centralized validation functions to ensure consistency across the application
"""
import re
from typing import Tuple


def is_valid_email(email: str) -> bool:
    """
    Validate email format using RFC 5322 compliant regex
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    Requirements: minimum 6 characters, at least one uppercase letter.
    """
    # FIX: was checking isinstance(email, str) — wrong variable name
    if not password or not isinstance(password, str):
        return False, "Password is required"

    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    return True, ""


def validate_hours(productive: float, non_productive: float) -> Tuple[bool, str]:
    """
    Validate timesheet hours
    """
    try:
        prod = float(productive)
        non_prod = float(non_productive)

        if prod < 0:
            return False, "Productive hours cannot be negative"
        if non_prod < 0:
            return False, "Non-productive hours cannot be negative"
        if prod > 24:
            return False, "Productive hours cannot exceed 24"
        if non_prod > 24:
            return False, "Non-productive hours cannot exceed 24"
        if (prod + non_prod) > 24:
            return False, "Total hours cannot exceed 24"

        return True, ""
    except (ValueError, TypeError):
        return False, "Invalid hour format"


def sanitize_text(text: str, max_length: int = None) -> str:
    """
    Sanitize text input to prevent XSS and injection attacks
    """
    if not text:
        return text

    import bleach

    # Remove all HTML tags and strip whitespace
    sanitized = bleach.clean(str(text), tags=[], strip=True)

    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized.strip()


def validate_file_size(file_size: int, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate uploaded file size
    """
    max_bytes = max_size_mb * 1024 * 1024

    if file_size > max_bytes:
        return False, f"File size exceeds maximum allowed size of {max_size_mb}MB"

    return True, ""


def validate_file_extension(filename: str, allowed_extensions: list) -> Tuple[bool, str]:
    """
    Validate file extension
    """
    if not filename or '.' not in filename:
        return False, "Invalid filename"

    ext = '.' + filename.rsplit('.', 1)[1].lower()

    if ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    return True, ""
