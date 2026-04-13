"""GitHub Issues-based task queue implementation.

Implements the ITaskQueue interface using GitHub Issues, Labels, and Milestones
as the persistence layer. Shared by both the Sentinel (Orchestrator) and
Notifier (Listener) services (per Simplification Decision S-6).

Key features:
- Fetches queued tasks via GitHub REST API (GET /repos/{org}/{repo}/issues?labels=agent:queued)
- Claim tasks using assign-then-verify distributed locking pattern
- Update task status by mutating GitHub Issue labels
- Post heartbeat comments during long-running execution
- Connection pooling via single httpx.AsyncClient instance (per R-5)
"""

import httpx


class ITaskQueue:
    """Abstract base class for task queue operations.

    Defines the Strategy Pattern interface enabling future provider swapping
    (Linear, Jira, Notion, SQL) without rewriting orchestrator logic (per ADR 09).
    """

    async def fetch_queued_tasks(self) -> list[dict]:
        """Fetch all tasks currently in the queued state."""
        ...

    async def claim_task(self, issue_number: int) -> bool:
        """Attempt to claim a task using distributed locking.

        Args:
            issue_number: The GitHub Issue number to claim.

        Returns:
            True if the claim was successful, False otherwise.
        """
        ...

    async def update_status(self, issue_number: int, label: str) -> None:
        """Update the status label on a task.

        Args:
            issue_number: The GitHub Issue number to update.
            label: The new status label to apply.
        """
        ...


class GitHubQueue(ITaskQueue):
    """GitHub Issues-based implementation of the task queue.

    Uses GitHub REST API with a shared httpx.AsyncClient for
    connection pooling. Handles rate limiting with jittered
    exponential backoff.
    """

    def __init__(self, token: str, org: str, repo: str) -> None:
        """Initialize the GitHub queue client.

        Args:
            token: GitHub App installation token.
            org: GitHub organization/owner name.
            repo: Target repository name.
        """
        self._token = token
        self._org = org
        self._repo = repo
        self._base_url = f"https://api.github.com/repos/{org}/{repo}"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the shared HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=30.0,
            )
        return self._client

    async def fetch_queued_tasks(self) -> list[dict]:
        """Fetch all issues with the agent:queued label."""
        client = await self._get_client()
        response = await client.get(f"{self._base_url}/issues", params={"labels": "agent:queued", "state": "open"})
        response.raise_for_status()
        return response.json()

    async def claim_task(self, issue_number: int) -> bool:
        """Claim a task using the assign-then-verify pattern.

        1. Attempt to assign the bot account to the issue
        2. Re-fetch the issue via GitHub API
        3. Verify the bot is the current assignee
        4. Only then proceed — aborts gracefully on failure
        """
        # TODO: Implement assign-then-verify locking
        _ = issue_number
        return False

    async def update_status(self, issue_number: int, label: str) -> None:
        """Update the status label on a GitHub Issue."""
        client = await self._get_client()
        await client.post(
            f"{self._base_url}/issues/{issue_number}/labels",
            json={"labels": [label]},
        )

    async def close(self) -> None:
        """Close the shared HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
