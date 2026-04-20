# OS-APOW Architecture Document

> **Project:** workflow-orchestration-queue (OS-APOW — Opencode-Server Agent Workflow Orchestration)
> **Last Updated:** 2026-04-13
> **Source Documents:** Architecture Guide v3.2, Development Plan v4.2, Plan Review, Simplification Report v1

---

## 1. Executive Summary

**workflow-orchestration-queue** is a headless agentic orchestration platform that transforms GitHub Issues into autonomous "Execution Orders" fulfilled by specialized AI agents. The system shifts the AI paradigm from an interactive co-pilot (requiring human-in-the-loop prompting) to an autonomous background production service — a tireless junior developer on your team.

The architecture is strictly decoupled and event-driven, distributed across **four conceptual pillars** (The Ear, The State, The Brain, The Hands), each handling a distinct domain. The system is **self-bootstrapping**: Phase 1 is manually seeded, then the orchestrator builds subsequent phases using its own agentic workflows.

---

## 2. System Architecture — The Four Pillars

### 2A. The Ear (Work Event Notifier)

**Technology:** Python 3.12, FastAPI, Uvicorn, Pydantic

**Responsibility:** High-performance webhook receiver serving as the system's sensory input layer.

| Aspect | Detail |
|--------|--------|
| **Endpoint** | `POST /webhooks/github` |
| **Security** | HMAC SHA-256 signature verification on all requests — rejects unauthorized payloads with 401 before any JSON parsing |
| **Event Types** | `issues` (opened), `issue_comment`, `pull_request_review` (Phase 3) |
| **Triage Logic** | Parses issue titles/bodies to detect templates (`[Application Plan]`, `[Bugfix]`, etc.), maps to `TaskType` enum, applies `agent:queued` label via GitHub API |
| **Response** | Returns `202 Accepted` to GitHub within the 10-second timeout |
| **API Docs** | Auto-generated Swagger/OpenAPI at `/docs` |
| **Health Check** | `GET /health` — returns `{"status": "online", "system": "OS-APOW Notifier"}` |

**Key Implementation File:** `src/notifier_service.py`

### 2B. The State (Work Queue)

**Technology:** GitHub Issues, Labels, Milestones (no external database)

**Philosophy:** "Markdown as a Database" — task state is stored entirely in GitHub Issues via labels, providing perfect transparency, world-class audit logs, and an out-of-the-box UI for human supervision.

**State Machine (Label Logic):**

```
                    ┌─────────────────┐
                    │  agent:queued   │ ◄─── Notifier applies this label
                    └────────┬────────┘
                             │ Sentinel claims via assign-then-verify
                             ▼
                    ┌─────────────────┐
                    │ agent:in-progress│ ◄─── Issue assigned to bot account
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
        ┌──────────┐  ┌──────────┐  ┌────────────────┐
        │agent:    │  │agent:    │  │agent:infra-    │
        │success   │  │error     │  │failure         │
        └──────────┘  └──────────┘  └────────────────┘
```

| State | Label | Description |
|-------|-------|-------------|
| QUEUED | `agent:queued` | Task validated, awaiting Sentinel pickup |
| IN_PROGRESS | `agent:in-progress` | Sentinel claimed the issue (assigned to bot account) |
| RECONCILING | `agent:reconciling` | Stale task identified by reconciliation loop (Phase 3) |
| SUCCESS | `agent:success` | Terminal — PR created, tests passed |
| ERROR | `agent:error` | Terminal — agent execution error (stderr posted as comment) |
| INFRA_FAILURE | `agent:infra-failure` | Terminal — container crash, build failure, timeout |
| STALLED_BUDGET | `agent:stalled-budget` | Terminal — cost guardrail exceeded (Phase 3) |

**Concurrency Control:** GitHub "Assignees" used as a distributed lock semaphore via the **assign-then-verify pattern**:
1. Sentinel attempts to assign its bot account (`SENTINEL_BOT_LOGIN`) to the issue
2. Sentinel re-fetches the issue via GitHub API
3. Sentinel verifies it is the current assignee
4. Only then proceeds — if verification fails, aborts gracefully

**Key Implementation File:** `src/queue/github_queue.py` — `GitHubQueue` class implementing `ITaskQueue` ABC

### 2C. The Brain (Sentinel Orchestrator)

**Technology:** Python 3.12 (async), Docker CLI, PowerShell Core

**Responsibility:** Persistent supervisor managing the lifecycle of Worker environments — maps high-level intent to low-level shell commands.

**Lifecycle (per task):**

```
1. POLL ──► 2. CLAIM ──► 3. UP ──► 4. START ──► 5. PROMPT ──► 6. FINALIZE ──► 7. STOP
   │            │           │         │             │              │              │
   │  assign-   │  devcont- │  open-  │  Execute    │  Label issue  │  Reset env
   │  then-     │  ainer-   │  code   │  workflow   │  success/    │  between
   │  verify    │  opencode │  server │  via shell  │  error       │  tasks
   │  locking   │  .sh up   │         │  bridge     │              │
```

| Step | Command | Timeout | Purpose |
|------|---------|---------|---------|
| Poll | GitHub API (`GET /repos/{org}/{repo}/issues?labels=agent:queued`) | 30s (HTTPX) | Discover new tasks |
| Claim | Assign + verify + label mutation | — | Acquire distributed lock |
| Up | `./scripts/devcontainer-opencode.sh up` | 300s | Provision Docker network and base volumes |
| Start | `./scripts/devcontainer-opencode.sh start` | 120s | Launch opencode-server inside DevContainer |
| Prompt | `./scripts/devcontainer-opencode.sh prompt "{instruction}"` | 5700s (95 min) | Execute AI workflow — **safety net timeout higher than inner watchdog's 5400s** |
| Finalize | Label mutation + comment post | — | Report success or error to GitHub |
| Stop | `./scripts/devcontainer-opencode.sh stop` | 60s | Reset environment between tasks |

**Key Features:**

- **Jittered Exponential Backoff:** On HTTP 403/429, backoff doubles with random jitter. Max backoff: 960s (16 min). Resets to base `POLL_INTERVAL` (60s) on successful poll.
- **Heartbeat Coroutine:** Background `asyncio.create_task()` posts status comments every 5 minutes (`HEARTBEAT_INTERVAL`) during long-running prompt execution. Critical for tasks exceeding 15+ minutes.
- **Graceful Shutdown:** Handles `SIGTERM` and `SIGINT` via signal handler. Sets `_shutdown_requested` flag — current task finishes, then exits cleanly. Prevents orphaned `agent:in-progress` issues.
- **Workflow Mapping:** Translates `TaskType` to instruction modules: `PLAN → create-app-plan.md`, `IMPLEMENT → perform-task.md`, `BUGFIX → recover-from-error.md`
- **Unique Instance ID:** Each Sentinel generates `sentinel-{uuid}` on startup for log tracing and attribution

**Key Implementation File:** `src/orchestrator_sentinel.py`

### 2D. The Hands (Opencode Worker)

**Technology:** opencode-server CLI, LLM Core (GLM-5), DevContainers

**Responsibility:** Isolated execution environment where actual coding happens.

| Aspect | Detail |
|--------|--------|
| **Environment** | High-fidelity DevContainer — bit-for-bit identical to human developer environments |
| **Network** | Segregated Docker bridge network — no access to host subnets or peer containers |
| **Resources** | Hard-capped at 2 CPUs, 4GB RAM |
| **Credentials** | Ephemeral env vars — injected by Sentinel, destroyed on container exit, never written to disk |
| **Instruction Logic** | Reads and executes Markdown workflow modules from `/local_ai_instruction_modules/` — "Logic-as-Markdown" principle |
| **Verification** | Runs local test suites before submitting PR to ensure zero-regression code generation |

---

## 3. Key Architectural Decisions (ADRs)

### ADR 07: Standardized Shell-Bridge Execution

**Decision:** The Orchestrator interacts with the agentic environment *exclusively* via `./scripts/devcontainer-opencode.sh`.

**Rationale:** The shell infrastructure handles complex Docker logic (volume mounting, SSH-agent forwarding, port mapping). Reimplementing in Python would cause configuration drift. Shell scripts guarantee perfect environment parity between AI workers and human developers.

**Consequence:** Python code stays lightweight (logic/state), shell scripts handle infra. Clear separation of concerns.

### ADR 08: Polling-First Resiliency Model

**Decision:** Sentinel uses polling as primary discovery; webhooks are an optimization.

**Rationale:** Webhooks are fire-and-forget — if the server is down during an event, it's lost forever. Polling ensures state reconciliation on every restart via GitHub labels. Self-healing by design.

### ADR 09: Provider-Agnostic Interface Layer

**Decision:** All queue interactions abstracted behind `ITaskQueue` ABC using Strategy Pattern.

**Rationale:** Phase 1 targets GitHub, but the interface enables future provider swapping (Linear, Jira, Notion, SQL) without rewriting orchestrator logic. Interface methods: `add_to_queue()`, `fetch_queued_tasks()`, `update_status()`, plus Sentinel-specific `claim_task()` and `post_heartbeat()`.

**Simplification Decision (S-1):** ABC retained per user preference — provides stepping stone to future provider support.

---

## 4. Data Flow — The "Happy Path"

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  User   │───►│  Ear    │───►│  State  │───►│  Brain  │───►│  Hands  │
│ opens   │    │ verifies │    │ queued  │    │ claims  │    │ executes│
│ issue   │    │ HMAC     │    │ label   │    │ task    │    │ workflow│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                                  │
                    ┌─────────────────────────────────────────────┘
                    ▼
              ┌──────────┐    ┌──────────┐
              │  Brain   │───►│  State   │
              │ reports  │    │ success/ │
              │ result   │    │ error    │
              └──────────┘    └──────────┘
```

1. **Stimulus:** User opens a GitHub Issue with specific template
2. **Notification:** GitHub Webhook hits the Notifier (FastAPI)
3. **Triage:** Notifier verifies HMAC signature, confirms title pattern, applies `agent:queued` label
4. **Claim:** Sentinel poller detects the label, performs assign-then-verify, transitions to `agent:in-progress`
5. **Sync:** Sentinel runs `git clone`/`git pull` on target repo into managed workspace
6. **Environment:** Sentinel executes `devcontainer-opencode.sh up`
7. **Dispatch:** Sentinel sends prompt: `devcontainer-opencode.sh prompt "Run workflow: {module}"`
8. **Execution:** Worker reads issue, analyzes codebase, implements solution, runs tests
9. **Finalize:** Worker posts completion comment; Sentinel detects exit code, labels issue `agent:success`

---

## 5. Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # Core definition: uv dependencies, metadata, scripts
├── uv.lock                      # Deterministic lockfile for exact package versions
├── src/
│   ├── __init__.py
│   ├── notifier_service.py      # FastAPI Webhook ingestion and event routing
│   ├── orchestrator_sentinel.py # Background polling, locking, and dispatch
│   ├── models/
│   │   ├── __init__.py
│   │   └── work_item.py         # Unified WorkItem, TaskType, WorkItemStatus, scrub_secrets()
│   └── queue/
│       ├── __init__.py
│       └── github_queue.py      # ITaskQueue ABC + GitHubQueue (shared by sentinel & notifier)
├── scripts/                     # Shell Bridge execution layer
│   ├── devcontainer-opencode.sh # Core orchestrator invoking the worker Docker context
│   ├── gh-auth.ps1              # PowerShell GitHub App auth synchronization
│   ├── common-auth.ps1          # Shared GitHub auth helper
│   └── update-remote-indices.ps1# Remote instruction module index sync
├── local_ai_instruction_modules/ # Decoupled Markdown logic workflows for the LLM
│   ├── create-app-plan.md       # Prompts for mapping out a new application
│   ├── perform-task.md          # Standard operational instructions
│   └── analyze-bug.md           # Stack trace analysis and fix instructions
├── tests/                       # Test suite
│   ├── test_sentinel.py         # Sentinel unit/integration tests
│   ├── test_notifier.py         # Notifier unit/integration tests
│   ├── test_work_item.py        # Data model and scrubber tests
│   └── test_github_queue.py     # Queue implementation tests
├── docs/                        # Architecture and user documentation
├── .github/                     # GitHub Actions workflows, issue templates, labels
├── .devcontainer/               # DevContainer configuration
└── plan_docs/                   # Seeded plan documents (not part of application)
```

---

## 6. Security Architecture

### Webhook Security
- All incoming webhooks validated via HMAC SHA-256 (`X-Hub-Signature-256`)
- Invalid signatures rejected with 401 before any JSON parsing
- Prevents prompt injection via spoofed payloads

### Credential Management
- **No hardcoded secrets** — all credentials via environment variables
- **Ephemeral tokens** — injected as in-memory env vars, destroyed on container exit
- **Credential scrubbing** — `scrub_secrets()` regex strips GitHub PATs, Bearer tokens, API keys from all public-facing output
- **Dual logging** — raw logs (local forensic "black box") + sanitized logs (public GitHub comments)

### Network Isolation
- Worker containers run in segregated Docker bridge network
- Cannot access host subnets, metadata endpoints (AWS IMDS), or peer containers
- Prevents lateral movement from compromised workers

### Resource Constraints
- 2 CPU, 4GB RAM hard limit per worker container
- Prevents rogue agent from causing host-level denial-of-service

### Environment Variable Validation
- Both Sentinel and Notifier validate required env vars at startup
- Crash immediately with clear error if missing or set to placeholder values
- Never embed secrets as defaults in source code

---

## 7. Simplification Decisions (Applied)

The following simplifications from the Plan Review and Simplification Report have been incorporated into the architecture:

| ID | Decision | Impact |
|----|----------|--------|
| S-3 | Only 3 required env vars (`GITHUB_TOKEN`, `GITHUB_ORG`, `GITHUB_REPO`) | Reduces `.env` surface by 70% |
| S-4 | Hardcoded `"stop"` environment reset mode | Removes 3-mode branching complexity |
| S-5 | Single-repo polling only (cross-repo deferred to future phase) | Eliminates Search API format branching |
| S-6 | Consolidated queue class (`GitHubQueue`) shared by sentinel & notifier | Eliminates stub code and class duplication |
| S-7 | No IPv4 address scrubbing (removed overly broad regex) | Prevents false positives on version strings |
| S-8 | No encryption verbiage for log files | Plain local log files sufficient for MVP |
| S-9 | Phase 3 features moved to Future Work appendix | Keeps Implementation Spec focused on current scope |
| S-10 | Stdout-only logging (no FileHandler) | `docker logs` or log aggregator handles persistence |
| S-11 | No `raw_payload` field on WorkItem | Removes unused field from data model |

---

## 8. Plan Review Fixes (To Implement)

| ID | Fix | Component | Status |
|----|-----|-----------|--------|
| R-1 | Heartbeat coroutine (`_heartbeat_loop`) | Sentinel | Reference implementation ready |
| R-2 | Assign-then-verify distributed locking | Sentinel → Queue | Reference implementation ready |
| R-3 | Unified data model in `src/models/work_item.py` | Both | Reference implementation ready |
| R-4 | Graceful shutdown (`SIGTERM`/`SIGINT` handler) | Sentinel | Reference implementation ready |
| R-5 | Connection pooling (single `httpx.AsyncClient`) | Queue | Reference implementation ready |
| R-6 | Env var validation at startup | Notifier | Reference implementation ready |
| R-7 | Credential scrubber (`scrub_secrets()`) | Models | Reference implementation ready |
| R-8 | Subprocess timeout safety net (5700s) | Sentinel | Reference implementation ready |

---

## 9. Self-Bootstrapping Lifecycle

The system is designed to build itself iteratively:

1. **Bootstrap:** Developer manually clones the template repository
2. **Seed:** Developer adds plan docs and runs the `create-repo-from-plan-docs` script
3. **Init:** Developer runs `devcontainer-opencode.sh up` for the first time
4. **Orchestrate:** Developer runs the `orchestrate-dynamic-workflow` command with the `project-setup` assignment — the agent configures its own environment
5. **Autonomous:** Once initialized, the Sentinel service runs on the server and the AI manages all further development

---

## 10. Future Work (Deferred to Phase 3+)

These features are architecturally accounted for but not in scope for Phase 1-2:

- **Hierarchical Task Delegation:** Architect Sub-Agent decomposes Epics into child issues with dependency ordering
- **Self-Healing Reconciliation Loop:** Automatic recovery of "zombie" tasks stuck in `agent:in-progress` beyond a timeout threshold
- **Cost Guardrails:** Token/budget monitoring with `agent:stalled-budget` state
- **Cross-Repo Org-Wide Polling:** GitHub Search API for multi-repo task discovery
- **Autonomous Bug Correction Loop:** PR review comment detection and automatic re-queue
- **Configurable Environment Reset Modes:** Three-mode teardown (`none`/`stop`/`down`)
