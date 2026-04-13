"""Tests for OS-APOW application configuration."""

import os

import pytest


def test_settings_import():
    """Verify the Settings class can be imported."""
    from osapow.config import Settings

    assert Settings is not None


def test_settings_requires_env_vars():
    """Verify Settings raises error when required env vars are missing."""
    from pydantic import ValidationError

    from osapow.config import Settings

    # Clear env vars to ensure test isolation
    env_keys = ["GITHUB_TOKEN", "GITHUB_ORG", "GITHUB_REPO"]
    saved = {k: os.environ.pop(k, None) for k in env_keys}

    try:
        with pytest.raises(ValidationError):
            Settings()
    finally:
        # Restore env vars
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
