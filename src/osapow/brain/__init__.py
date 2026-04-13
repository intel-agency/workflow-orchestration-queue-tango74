"""Brain (Orchestrator) service — task decomposition and agent coordination.

The Brain pillar is the persistent supervisor managing the lifecycle of
Worker environments. It maps high-level intent to low-level shell commands.

Lifecycle per task:
1. POLL — Discover new tasks via GitHub API
2. CLAIM — Acquire distributed lock via assign-then-verify
3. UP — Provision Docker network and base volumes
4. START — Launch opencode-server inside DevContainer
5. PROMPT — Execute AI workflow via shell bridge
6. FINALIZE — Label issue success/error
7. STOP — Reset environment between tasks
"""
