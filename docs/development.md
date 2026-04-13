# OS-APOW Development Guide

## Prerequisites

- **Python 3.12+** (checked via `.python-version`)
- **uv** package manager — [install guide](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker** (optional, for containerized development)

## Quick Start

### 1. Install dependencies

```bash
uv sync --dev
```

### 2. Run the development server

```bash
uv run uvicorn osapow.main:app --reload
```

The API will be available at http://localhost:8000 with:
- Health check: `GET /health`
- API docs: `GET /docs` (Swagger UI)

### 3. Run tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=osapow --cov-report=term-missing

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/
```

### 4. Lint and type check

```bash
# Lint with ruff
uv run ruff check src/ tests/

# Format check
uv run ruff format --check src/ tests/

# Type check with mypy
uv run mypy src/
```

## Project Structure

```
src/osapow/
├── __init__.py          # Package root
├── main.py              # FastAPI entry point
├── config.py            # Pydantic Settings
├── ear/                 # Listener service (webhook intake)
├── state/               # Queue service (GitHub Issues)
├── brain/               # Orchestrator service (task lifecycle)
├── hands/               # Executor service (shell-bridge)
└── common/              # Shared utilities (logging, secrets)
tests/
├── conftest.py          # Shared fixtures
├── test_config.py       # Configuration tests
├── unit/                # Unit tests
└── integration/         # Integration tests
```

## Docker

### Build and run

```bash
docker compose up --build
```

### Health check

```bash
curl http://localhost:8000/health
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub App installation token |
| `GITHUB_ORG` | Yes | GitHub organization/owner |
| `GITHUB_REPO` | Yes | Target repository name |
| `WEBHOOK_SECRET` | Notifier | HMAC secret for webhook verification |
| `SENTINEL_BOT_LOGIN` | Optional | Bot account for assign-then-verify |

## CI/CD

The CI pipeline (`.github/workflows/ci.yml`) runs on push to `main` and on PRs:

1. **Lint** — ruff check
2. **Type check** — mypy
3. **Test** — pytest
4. **Docker build** — verifies the Dockerfile builds successfully
