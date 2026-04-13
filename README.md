# OS-APOW

**Orchestration System — Automated Pipeline Orchestration Workflow**

A headless agentic orchestration platform that transforms GitHub Issues into
autonomous "Execution Orders" fulfilled by specialized AI agents.

> **Repository Summary:** See [.ai-repository-summary.md](.ai-repository-summary.md) for the full project overview.

## Architecture — The Four Pillars

| Pillar     | Service        | Responsibility                                    |
|------------|----------------|---------------------------------------------------|
| **Ear**    | Listener       | Webhook intake and event triage (FastAPI)          |
| **State**  | Queue          | Task management via GitHub Issues ("Markdown as DB") |
| **Brain**  | Orchestrator   | Task decomposition and agent coordination (Sentinel) |
| **Hands**  | Executor       | Shell-bridge execution in isolated DevContainers   |

## Tech Stack

- **Python 3.12+** with **uv** package manager
- **FastAPI** + **Uvicorn** for API services
- **Pydantic v2** for data models and settings
- **HTTPX** for async HTTP client
- **Docker** for containerization
- **GitHub Actions** for CI/CD

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker (optional)

### Install and Run

```bash
# Install dependencies
uv sync --dev

# Run the development server
uv run uvicorn osapow.main:app --reload
```

The API is available at http://localhost:8000:
- Health check: `GET /health`
- API docs: `GET /docs`

### Docker

```bash
docker compose up --build
```

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=osapow --cov-report=term-missing

# Unit tests only
uv run pytest tests/unit/
```

### Lint and Type Check

```bash
uv run ruff check src/ tests/
uv run mypy src/
```

## Project Structure

```
src/osapow/
├── __init__.py          # Package root
├── main.py              # FastAPI entry point
├── config.py            # Pydantic Settings
├── ear/                 # Listener service (webhook intake)
│   ├── webhook.py       # Webhook handler
│   └── triage.py        # Event triage and TaskType mapping
├── state/               # Queue service (GitHub Issues)
│   ├── queue.py         # ITaskQueue ABC + GitHubQueue
│   └── models.py        # WorkItem, WorkItemStatus
├── brain/               # Orchestrator service (task lifecycle)
│   ├── orchestrator.py  # Sentinel supervisor
│   └── decomposer.py    # Task-to-workflow mapping
├── hands/               # Executor service (shell-bridge)
│   └── executor.py      # DevContainer execution manager
└── common/              # Shared utilities
    ├── logging.py       # Structured logging configuration
    └── secrets.py       # Credential scrubbing
tests/
├── conftest.py          # Shared fixtures
├── test_config.py       # Configuration tests
├── unit/                # Unit tests
└── integration/         # Integration tests
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub App installation token |
| `GITHUB_ORG` | Yes | GitHub organization/owner |
| `GITHUB_REPO` | Yes | Target repository name |
| `WEBHOOK_SECRET` | Notifier | HMAC secret for webhook verification |
| `SENTINEL_BOT_LOGIN` | Optional | Bot account for assign-then-verify |

## Documentation

- [Architecture](docs/architecture.md) — links to the canonical architecture spec
- [Development Guide](docs/development.md) — setup, testing, and development instructions
- [plan_docs/](plan_docs/) — seeded plan documents and reference implementations

## License

See [LICENSE](LICENSE) for details.
