"""Tests for OS-APOW task queue (GitHubQueue)."""


import pytest


class TestGitHubQueue:
    """Tests for the GitHubQueue implementation."""

    @pytest.mark.asyncio
    async def test_queue_import(self):
        """Verify GitHubQueue can be imported."""
        from osapow.state.queue import GitHubQueue

        assert GitHubQueue is not None

    @pytest.mark.asyncio
    async def test_queue_init(self):
        """Verify GitHubQueue initializes with correct attributes."""
        from osapow.state.queue import GitHubQueue

        queue = GitHubQueue(token="fake-token", org="test-org", repo="test-repo")
        assert queue._org == "test-org"
        assert queue._repo == "test-repo"
        assert "test-org" in queue._base_url
        assert "test-repo" in queue._base_url

    @pytest.mark.asyncio
    async def test_queue_close(self):
        """Verify queue closes cleanly when no client is active."""
        from osapow.state.queue import GitHubQueue

        queue = GitHubQueue(token="fake-token", org="test-org", repo="test-repo")
        await queue.close()  # Should not raise
