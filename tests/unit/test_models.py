"""Tests for OS-APOW data models (WorkItem, WorkItemStatus, TaskType)."""

from osapow.ear.triage import TaskType
from osapow.state.models import WorkItem, WorkItemStatus


class TestWorkItemStatus:
    """Tests for the WorkItemStatus enum."""

    def test_queued_status(self):
        """Verify QUEUED maps to agent:queued label."""
        assert WorkItemStatus.QUEUED == "agent:queued"

    def test_in_progress_status(self):
        """Verify IN_PROGRESS maps to agent:in-progress label."""
        assert WorkItemStatus.IN_PROGRESS == "agent:in-progress"

    def test_success_status(self):
        """Verify SUCCESS maps to agent:success label."""
        assert WorkItemStatus.SUCCESS == "agent:success"

    def test_error_status(self):
        """Verify ERROR maps to agent:error label."""
        assert WorkItemStatus.ERROR == "agent:error"

    def test_infra_failure_status(self):
        """Verify INFRA_FAILURE maps to agent:infra-failure label."""
        assert WorkItemStatus.INFRA_FAILURE == "agent:infra-failure"


class TestTaskType:
    """Tests for the TaskType enum."""

    def test_plan_type(self):
        """Verify PLAN task type exists."""
        assert TaskType.PLAN == "plan"

    def test_implement_type(self):
        """Verify IMPLEMENT task type exists."""
        assert TaskType.IMPLEMENT == "implement"

    def test_bugfix_type(self):
        """Verify BUGFIX task type exists."""
        assert TaskType.BUGFIX == "bugfix"


class TestWorkItem:
    """Tests for the WorkItem Pydantic model."""

    def test_create_work_item(self):
        """Verify WorkItem can be created with required fields."""
        item = WorkItem(
            id="test-123",
            issue_number=42,
            source_url="https://github.com/test/repo/issues/42",
            context_body="Test task body",
            target_repo_slug="test-repo",
            task_type="implement",
        )
        assert item.id == "test-123"
        assert item.issue_number == 42
        assert item.status == WorkItemStatus.QUEUED

    def test_work_item_default_status(self):
        """Verify WorkItem defaults to QUEUED status."""
        item = WorkItem(
            id="test-456",
            issue_number=1,
            source_url="https://github.com/test/repo/issues/1",
            context_body="Body",
            target_repo_slug="repo",
            task_type="plan",
        )
        assert item.status == WorkItemStatus.QUEUED
