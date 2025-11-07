# tests/unit/test_utils.py

import pytest
from app.utils.validators import (
    validate_email,
    validate_url,
    validate_slug,
    is_valid_youtube_url,
    is_valid_github_url
)
from app.utils.helpers import (
    slugify,
    sanitize_html,
    truncate_text,
    parse_tags,
    tags_to_string
)


class TestValidators:
    
    def test_validate_email(self):
        assert validate_email("test@example.com") is True
        assert validate_email("invalid.email") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False
    
    def test_validate_url(self):
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("ftp://example.com") is False
        assert validate_url("not-a-url") is False
        assert validate_url("") is False
    
    def test_validate_slug(self):
        assert validate_slug("valid-slug") is True
        assert validate_slug("another-valid-slug-123") is True
        assert validate_slug("Invalid_Slug") is False
        assert validate_slug("invalid slug") is False
        assert validate_slug("invalid-slug-") is False
    
    def test_is_valid_youtube_url(self):
        assert is_valid_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert is_valid_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True
        assert is_valid_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ") is True
        assert is_valid_youtube_url("https://example.com") is False
    
    def test_is_valid_github_url(self):
        assert is_valid_github_url("https://github.com/user/repo") is True
        assert is_valid_github_url("http://github.com/user/repo") is True
        assert is_valid_github_url("https://gitlab.com/user/repo") is False


class TestHelpers:
    
    def test_slugify(self):
        assert slugify("Hello World") == "hello-world"
        assert slugify("Test Post 123") == "test-post-123"
        assert slugify("Special!@#Characters") == "specialcharacters"
        assert slugify("Multiple   Spaces") == "multiple-spaces"
    
    def test_sanitize_html(self):
        assert sanitize_html("<p>Hello</p>") == "Hello"
        assert sanitize_html("<script>alert('xss')</script>") == "alert('xss')"
        assert sanitize_html("No HTML") == "No HTML"
    
    def test_truncate_text(self):
        text = "This is a long text that needs truncation"
        assert len(truncate_text(text, 20)) <= 20
        assert truncate_text(text, 20).endswith("...")
        assert truncate_text("Short", 20) == "Short"
    
    def test_parse_tags(self):
        assert parse_tags("python, fastapi, testing") == ["python", "fastapi", "testing"]
        assert parse_tags("single") == ["single"]
        assert parse_tags("") == []
        assert parse_tags("  spaces  ,  trimmed  ") == ["spaces", "trimmed"]
    
    def test_tags_to_string(self):
        assert tags_to_string(["python", "fastapi"]) == "python, fastapi"
        assert tags_to_string([]) == ""
        assert tags_to_string(["single"]) == "single"