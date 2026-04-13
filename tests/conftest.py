"""Shared test fixtures and configuration for OS-APOW tests.

Provides common pytest fixtures used across unit and integration tests.
"""

import pytest
from fastapi.testclient import TestClient

from osapow.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI test client for API testing."""
    return TestClient(app)


@pytest.fixture
def sample_issue_payload() -> dict:
    """Provide a sample GitHub Issue webhook payload for testing."""
    return {
        "action": "opened",
        "issue": {
            "number": 42,
            "title": "[Application Plan] My New App",
            "body": "This is a test application plan.",
            "html_url": "https://github.com/test-org/test-repo/issues/42",
            "node_id": "ISSUE_test",
            "labels": [],
        },
        "repository": {
            "full_name": "test-org/test-repo",
            "owner": {"login": "test-org"},
            "name": "test-repo",
        },
    }
