"""State (Queue) service — task management via GitHub Issues.

The State pillar uses "Markdown as a Database" — task state is stored
entirely in GitHub Issues via labels, providing perfect transparency,
world-class audit logs, and an out-of-the-box UI for human supervision.

State Machine (Label Logic):
    agent:queued → agent:in-progress → agent:success | agent:error | agent:infra-failure

Concurrency Control:
    GitHub "Assignees" used as a distributed lock semaphore via the
    assign-then-verify pattern.
"""
