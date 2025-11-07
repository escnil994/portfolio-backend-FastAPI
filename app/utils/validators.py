# app/utils/validators.py

import re
from urllib.parse import urlparse
from typing import Optional


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str, allowed_schemes: Optional[list] = None) -> bool:
    if not url:
        return False
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    try:
        result = urlparse(url)
        return (
            result.scheme in allowed_schemes
            and bool(result.netloc)
            and len(url) <= 2000
        )
    except Exception:
        return False


def validate_slug(slug: str) -> bool:
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug)) and len(slug) <= 255


def is_valid_youtube_url(url: str) -> bool:
    youtube_patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
    ]
    return any(re.match(pattern, url) for pattern in youtube_patterns)


def is_valid_github_url(url: str) -> bool:
    pattern = r'^https?://github\.com/[\w-]+/[\w.-]+'
    return bool(re.match(pattern, url))


def is_valid_linkedin_url(url: str) -> bool:
    pattern = r'^https?://(?:www\.)?linkedin\.com/in/[\w-]+'
    return bool(re.match(pattern, url))


def is_valid_twitter_url(url: str) -> bool:
    pattern = r'^https?://(?:www\.)?(?:twitter\.com|x\.com)/[\w]+'
    return bool(re.match(pattern, url))


def is_disposable_email(email: str) -> bool:
    disposable_domains = {
        'tempmail.com', 'guerrillamail.com', '10minutemail.com',
        'mailinator.com', 'throwaway.email', 'temp-mail.org',
        'yopmail.com', 'getnada.com', 'maildrop.cc'
    }
    
    domain = email.split('@')[-1].lower()
    return domain in disposable_domains


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, None