# AGENTS.md — OS-APOW Project Instructions

> This file provides AI coding agents with the context needed to work effectively on the OS-APOW project.

## Project Overview

**OS-APOW** (Orchestration System — Automated Pipeline Orchestration Workflow) is a headless agentic orchestration platform that transforms GitHub Issues into autonomous "Execution Orders" fulfilled by specialized AI agents. The system shifts the AI paradigm from an interactive co-pilot to an autonomous background production service.

**Repository:** `intel-agency/workflow-orchestration-queue-tango74`

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.12+ |
| Package Manager | uv | latest |
| Web Framework | FastAPI | 0.115+ |
| ASGI Server | Uvicorn | 0.34+ |
| Data Validation | Pydantic v2 | 2.10+ |
| Settings | pydantic-settings | 2.7+ |
| HTTP Client | HTTPX (async) | 0.28+ |
| Testing | pytest | 8.0+ |
| Async Testing | pytest-asyncio | 0.24+ |
| Test Coverage | pytest-cov | 6.0+ |
| Linting | ruff | 0.8+ |
| Type Checking | mypy | 1.13+ |
| Containerization | Docker, Docker Compose | — |
| CI/CD | GitHub Actions | — |

## Setup Commands

All commands assume the working directory is the repository root.

```bash
# Install dependencies (production only)
uv sync

# Install dependencies (including dev tools: pytest, ruff, mypy)
uv sync --extra dev

# Verify the package imports correctly
uv run python -c "import osapow; print(osapow.__version__)"
```

### Required Environment Variables

Set these in a `.env` file at the repository root (for local development):

```env
GITHUB_TOKEN=<GitHub App installation token>
GITHUB_ORG=<organization-or-owner>
GITHUB_REPO=<target-repository-name>
```

Optional variables:

- `WEBHOOK_SECRET` — HMAC secret for webhook signature verification
- `SENTINEL_BOT_LOGIN` — Bot account login for assign-then-verify locking
- `POLL_INTERVAL` — Seconds between Sentinel poll cycles (default: 60)

## Build and Run

```bash
# Run the FastAPI application locally
uv run uvicorn osapow.main:app --host 0.0.0.0 --port 8000 --reload

# Build and run with Docker Compose
docker compose up --build

# Run inside Docker (reads .env automatically)
docker compose up
```

The application exposes:
- **Health check:** `GET /health` — returns `{"status": "online", "system": "OS-APOW Notifier"}`
- **Webhook endpoint:** `POST /webhooks/github` — receives GitHub webhook events
- **API docs:** `GET /docs` — auto-generated Swagger UI

## Lint and Format

```bash
# Lint source and tests
uv run ruff check src/ tests/

# Auto-fix lint issues
uv run ruff check --fix src/ tests/

# Check formatting
uv run ruff format --check src/ tests/

# Apply formatting
uv run ruff format src/ tests/
```

**Ruff configuration** (in `pyproject.toml`):
- Target: Python 3.12
- Line length: 120
- Rule set: `E`, `F`, `I`, `N`, `W`, `UP`

## Type Checking

```bash
# Run mypy with strict mode
uv run mypy src/
```

**mypy configuration** (in `pyproject.toml`): `strict = true`, `python_version = "3.12"`

## Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=osapow --cov-report=term-missing

# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/

# List all test cases without running
uv run pytest --co -q
```

**pytest configuration** (in `pyproject.toml`):
- Test paths: `tests/`
- asyncio mode: `auto` (all async tests are auto-detected)

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures (TestClient, sample payloads)
├── test_config.py       # Settings import and validation tests
├── unit/
│   ├── test_models.py   # WorkItem, WorkItemStatus, TaskType tests
│   └── test_queue.py    # GitHubQueue initialization and lifecycle tests
└── integration/
    └── test_api.py       # API endpoint tests (health, webhook)
```

### Writing Tests

- Use `pytest-asyncio` for async tests (mode is `auto` — no explicit markers needed)
- Use `TestClient` from `conftest.py` for API endpoint tests
- Add new fixture payloads to `tests/conftest.py` or create fixture files
- Use `respx` for mocking HTTPX requests when testing API client code

## Project Structure

```
/
├── pyproject.toml           # Project definition, dependencies, tool config
├── uv.lock                  # Locked dependency versions
├── .python-version          # Python version pin (3.12)
├── Dockerfile               # Container build (python:3.12-slim + uv)
├── docker-compose.yml       # Local development (app + healthcheck)
├── README.md                # Project readme
├── AGENTS.md                # This file — agent instructions
├── .ai-repository-summary.md # Machine-readable project summary
│
├── src/osapow/              # Main application package
│   ├── __init__.py          # Package root, version (0.1.0)
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic Settings (env vars)
│   │
│   ├── ear/                 # Ear pillar — Listener service
│   │   ├── webhook.py       # GitHub webhook handler (POST /webhooks/github)
│   │   └── triage.py        # Event triage, TaskType enum
│   │
│   ├── state/               # State pillar — Queue service
│   │   ├── models.py        # WorkItem, WorkItemStatus models
│   │   └── queue.py         # ITaskQueue ABC, GitHubQueue implementation
│   │
│   ├── brain/               # Brain pillar — Orchestrator service
│   │   ├── orchestrator.py  # Sentinel supervisor (poll, claim, execute)
│   │   └── decomposer.py    # Task-to-workflow mapping
│   │
│   ├── hands/               # Hands pillar — Executor service
│   │   └── executor.py      # Shell-bridge DevContainer executor
│   │
│   └── common/              # Shared utilities
│       ├── logging.py       # Structured logging
│       └── secrets.py       # Secret management
│
├── tests/                   # Test suite
│   ├── conftest.py          # Shared fixtures
│   ├── test_config.py       # Config tests
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
│
├── docs/                    # Documentation
├── plan_docs/               # Seeded plan documents (do not lint)
├── scripts/                 # Helper scripts (PowerShell + Bash)
│
├── .github/workflows/       # CI/CD pipelines
│   ├── ci.yml               # Python lint, type check, test, Docker build
│   ├── validate.yml         # Repository validation
│   └── orchestrator-agent.yml # AI agent orchestration
│
├── .opencode/               # Agent definitions and commands
│   ├── agents/              # Specialist agent prompts
│   ├── commands/            # Reusable command prompts
│   └── opencode.json        # opencode CLI config (MCP servers)
│
├── .devcontainer/           # Consumer devcontainer (prebuilt GHCR image)
└── local_ai_instruction_modules/ # Markdown instruction modules
```

## Architecture: Four-Pillar Design

The system is organized around four conceptual pillars that map to distinct responsibilities:

### 1. Ear (Listener)
- **Entry point:** `src/osapow/ear/webhook.py` — FastAPI router at `/webhooks/github`
- **Triage:** `src/osapow/ear/triage.py` — parses issue templates, maps to `TaskType`
- **Purpose:** High-performance webhook receiver; verifies HMAC SHA-256 signatures, returns 202 Accepted within GitHub's timeout window, routes events to triage

### 2. State (Queue)
- **Models:** `src/osapow/state/models.py` — `WorkItem`, `WorkItemStatus` (Pydantic v2)
- **Queue:** `src/osapow/state/queue.py` — `ITaskQueue` (ABC) + `GitHubQueue` (GitHub Issues-based)
- **Pattern:** "Markdown as a Database" — uses GitHub Issues, Labels, Milestones as persistence
- **Concurrency:** Assign-then-verify distributed locking pattern

### 3. Brain (Orchestrator)
- **Sentinel:** `src/osapow/brain/orchestrator.py` — persistent supervisor
- **Decomposer:** `src/osapow/brain/decomposer.py` — maps `TaskType` to workflow instruction modules
- **Features:** Jittered exponential backoff (max 960s), heartbeat coroutine (5 min), graceful shutdown on SIGTERM/SIGINT

### 4. Hands (Executor)
- **Executor:** `src/osapow/hands/executor.py` — shell-bridge execution pattern (ADR 07)
- **Isolation:** DevContainer-based workers with network isolation and resource constraints (2 CPU, 4GB RAM)
- **Flow:** up → start → prompt → stop

### Key Architectural Decisions

- **ADR 07:** Shell-Bridge Execution — Orchestrator interacts via shell scripts only
- **ADR 08:** Polling-First Resiliency — Polling as primary discovery, webhooks as optimization
- **ADR 09:** Provider-Agnostic Interface — `ITaskQueue` ABC for future provider support (Linear, Jira, SQL)

## Code Style and Conventions

### Python Conventions

- **Python 3.12+** — use modern syntax (`type` unions, `StrEnum`, etc.)
- **Type hints required** on all function signatures (enforced by mypy strict mode)
- **Docstrings:** Use triple-quoted docstrings on all modules, classes, and public functions. Follow the Google-style format with `Args:` and `Returns:` sections
- **Async-first:** All I/O-bound operations use `async/await`
- **Pydantic v2 models** for all data validation — use `BaseModel` for schemas, `BaseSettings` for configuration

### Naming Conventions

- Modules: `snake_case.py`
- Classes: `PascalCase` (e.g., `GitHubQueue`, `WorkItem`, `Sentinel`)
- Functions/methods: `snake_case` (e.g., `fetch_queued_tasks`, `triage_event`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `WorkItemStatus.QUEUED`)
- Private members: prefix with `_` (e.g., `_get_client`, `_shutdown_requested`)

### Import Order

Enforced by ruff (`I` rule set):
1. Standard library
2. Third-party packages
3. Local application imports

### Error Handling

- Use `response.raise_for_status()` for HTTP errors
- Use `asyncio.wait_for()` with timeouts for subprocess operations
- Return exit code 124 on subprocess timeout (consistent with `timeout` command)
- Never swallow exceptions silently — at minimum, log them

### Secrets

- All secrets loaded from environment variables via `pydantic-settings`
- Never hardcode tokens, secrets, or API keys
- Never commit `.env` files
- `GITHUB_TOKEN` is provided automatically by GitHub Actions

## PR and Commit Guidelines

### Commit Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `build`

Examples:
```
feat(ear): add HMAC signature verification for webhooks
fix(queue): resolve race condition in assign-then-verify locking
docs: update AGENTS.md with testing instructions
test(state): add WorkItem model validation tests
ci: add Python lint and type-check workflow
```

### PR Guidelines

- Keep changes minimal and targeted
- Include tests for any new behavior or bug fixes
- Run `uv run ruff check src/ tests/` and `uv run pytest` before pushing
- All CI checks must pass before merge

## Common Pitfalls

### Environment Variables
- `Settings` will crash at import time if `GITHUB_TOKEN`, `GITHUB_ORG`, or `GITHUB_REPO` are missing. Set them in `.env` for local development or ensure they are present in CI.
- Tests that import `config.py` directly may need to mock or set these variables.

### asyncio Mode
- `pytest.ini_options.asyncio_mode = "auto"` means all async test functions are automatically wrapped — do not add `@pytest.mark.asyncio` decorators.

### Ruff Format vs Check
- `ruff check` catches lint errors (unused imports, naming, etc.)
- `ruff format` handles code formatting (line length, indentation)
- Both must pass: run `ruff check` then `ruff format --check`

### Docker Builds
- The `Dockerfile` uses `uv pip install --system -e .` — it does not install dev dependencies
- Docker Compose reads `.env` automatically via `env_file: .env`

### Import Paths
- The package is installed as `osapow` (not `src.osapow`)
- Always use `from osapow.xxx import yyy` (not `from src.osapow`)

### plan_docs/ Directory
- Contains externally-generated documents seeded at clone time
- Do not lint or reformat these files

## Verification Checklist

Run these before committing any non-trivial change:

```bash
# 1. Lint
uv run ruff check src/ tests/

# 2. Format check
uv run ruff format --check src/ tests/

# 3. Type check
uv run mypy src/

# 4. Tests
uv run pytest -v

# 5. Verify import
uv run python -c "import osapow"
```
