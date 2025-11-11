import re
from datetime import datetime, timezone
from typing import Optional
def validate_email_format(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
def validate_email_domain(email: str, allowed_domains: Optional[list[str]] = None) -> bool:
    if allowed_domains is None:
        return True
    domain = email.split('@')[-1]
    return domain in allowed_domains
def validate_name_length(name: str, min_length: int = 1, max_length: int = 100) -> bool:
    if not name or not isinstance(name, str):
        return False
    return min_length <= len(name.strip()) <= max_length
def validate_name_characters(name: str, allow_spaces: bool = True, allow_numbers: bool = True) -> bool:
    if not name or not isinstance(name, str):
        return False
    if allow_spaces and allow_numbers:
        pattern = r'^[\w\s]+$'
    elif allow_spaces and not allow_numbers:
        pattern = r'^[^\d\s][\w\s]*[^\d\s]$'
    elif not allow_spaces and allow_numbers:
        pattern = r'^[\w]+$'
    else:
        pattern = r'^[^\d][\w]*[^\d]$'
    try:
        return bool(re.match(pattern, name.strip()))
    except re.error:
        return False
def validate_username(username: str) -> bool:
    if not username or not isinstance(username, str):
        return False
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return bool(re.match(pattern, username))
def validate_board_name(name: str) -> bool:
    if not validate_name_length(name, min_length=1, max_length=100):
        return False
    pattern = r'^[\w\s\-]{1,100}$'
    return bool(re.match(pattern, name.strip()))
def validate_list_name(name: str) -> bool:
    if not validate_name_length(name, min_length=1, max_length=100):
        return False
    pattern = r'^[\w\s\-]{1,100}$'
    return bool(re.match(pattern, name.strip()))
def validate_card_name(name: str) -> bool:
    if not validate_name_length(name, min_length=1, max_length=200):
        return False
    pattern = r'^[\w\s\-]{1,200}$'
    return bool(re.match(pattern, name.strip()))
def validate_label_name(name: str) -> bool:
    if not validate_name_length(name, min_length=1, max_length=50):
        return False
    pattern = r'^[\w\s\-]{1,50}$'
    return bool(re.match(pattern, name.strip()))
def validate_comment_content(content: str) -> bool:
    if not content or not isinstance(content, str):
        return False
    return 1 <= len(content.strip()) <= 1000
def validate_past_date(date: datetime) -> bool:
    if not isinstance(date, datetime):
        return False
    if not date.tzinfo:
        date = date.replace(tzinfo=timezone.utc)
    return date <= datetime.now(timezone.utc)
def validate_future_date(date: datetime) -> bool:
    if not isinstance(date, datetime):
        return False
    if not date.tzinfo:
        date = date.replace(tzinfo=timezone.utc)
    return date > datetime.now(timezone.utc)
def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        return False
    if not start_date.tzinfo:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if not end_date.tzinfo:
        end_date = end_date.replace(tzinfo=timezone.utc)
    return start_date <= end_date
def validate_iso_format(date_string: str) -> bool:
    if not date_string or not isinstance(date_string, str):
        return False
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except (ValueError, TypeError, AttributeError):
        return False
def validate_color_hex(color: str) -> bool:
    if not color or not isinstance(color, str):
        return False
    pattern = r'^#[0-9a-fA-F]{6}$'
    return bool(re.match(pattern, color))