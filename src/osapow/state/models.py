"""Data models for the State (Queue) service.

Defines the unified data model for work items flowing through the system:
- WorkItemStatus: Enum mapping to GitHub Issue label states
- WorkItem: Pydantic model representing a task from discovery to completion

All models use Pydantic v2 for strict validation and JSON serialization.
"""

from enum import StrEnum

from pydantic import BaseModel


class WorkItemStatus(StrEnum):
    """Task status states, mapped to GitHub Issue labels."""

    QUEUED = "agent:queued"
    IN_PROGRESS = "agent:in-progress"
    RECONCILING = "agent:reconciling"
    SUCCESS = "agent:success"
    ERROR = "agent:error"
    INFRA_FAILURE = "agent:infra-failure"
    STALLED_BUDGET = "agent:stalled-budget"


class WorkItem(BaseModel):
    """Unified work item representing a task from discovery to completion.

    Tracks the lifecycle of a GitHub Issue as it flows through the system,
    from initial webhook receipt (Ear) through triage (State), orchestration
    (Brain), and execution (Hands).
    """

    id: str
    issue_number: int
    source_url: str
    context_body: str
    target_repo_slug: str
    task_type: str
    status: WorkItemStatus = WorkItemStatus.QUEUED
    node_id: str = ""
