"""Task decomposer — maps TaskType to workflow instruction modules.

Translates high-level task types to specific workflow modules:
- PLAN → create-app-plan.md
- IMPLEMENT → perform-task.md
- BUGFIX → recover-from-error.md

The decomposer reads Markdown instruction modules from the
local_ai_instruction_modules/ directory (Logic-as-Markdown principle).
"""


def map_task_to_workflow(task_type: str) -> str:
    """Map a TaskType to its corresponding workflow instruction module.

    Args:
        task_type: The type of task (plan, implement, bugfix).

    Returns:
        Path to the Markdown instruction module.
    """
    mapping = {
        "plan": "local_ai_instruction_modules/create-app-plan.md",
        "implement": "local_ai_instruction_modules/perform-task.md",
        "bugfix": "local_ai_instruction_modules/analyze-bug.md",
    }
    return mapping.get(task_type, "local_ai_instruction_modules/perform-task.md")


def decompose_task(task_type: str, context: str) -> str:
    """Decompose a task into an executable instruction prompt.

    Reads the appropriate workflow module and combines it with
    the task context to produce a complete instruction for the
    opencode worker.

    Args:
        task_type: The type of task.
        context: The task context (issue body, requirements, etc.).

    Returns:
        The assembled instruction prompt for the worker.
    """
    workflow_path = map_task_to_workflow(task_type)
    # TODO: Read workflow module and assemble prompt with context
    _ = workflow_path, context
    return ""
