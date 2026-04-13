"""Event triage — parses issue templates and maps to TaskType.

Triage logic inspects incoming GitHub Issues to determine their type:
- Detects template patterns in issue titles/bodies
- Maps to TaskType enum (PLAN, IMPLEMENT, BUGFIX)
- Applies the agent:queued label via GitHub API
- Logs triage decisions for audit purposes
"""

from enum import StrEnum


class TaskType(StrEnum):
    """Types of work items the system can process."""

    PLAN = "plan"
    IMPLEMENT = "implement"
    BUGFIX = "bugfix"


async def triage_event(payload: dict) -> None:
    """Triage a GitHub event payload and apply appropriate labels.

    Parses the issue title and body to detect task templates,
    determines the TaskType, and applies the agent:queued label.

    Args:
        payload: The parsed GitHub webhook event JSON.
    """
    # TODO: Implement triage logic
    # 1. Extract issue title and body from payload
    # 2. Match against template patterns ([Application Plan], [Bugfix], etc.)
    # 3. Map to TaskType
    # 4. Apply agent:queued label via GitHub API
    _ = payload  # suppress unused warning until implementation
