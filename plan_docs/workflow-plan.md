# Workflow Execution Plan: project-setup

**Workflow:** `project-setup`  
**Dynamic Workflow File:** `ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md`  
**Repository:** `intel-agency/workflow-orchestration-queue-tango74`  
**Date:** 2026-04-13  
**Status:** Approved for Execution  

---

## 1. Overview

The **project-setup** dynamic workflow orchestrates the initial setup of a new repository cloned from the `workflow-orchestration-queue-tango74` template. It is the first workflow executed after seeding the repository with plan documents. This workflow performs six sequential assignments that transform a bare template clone into a fully initialized, planned, and structured project ready for autonomous development.

**Project Name:** workflow-orchestration-queue (OS-APOW — Opencode-Server Agent Workflow Orchestration)  
**Total Assignments:** 6 (in execution order)  
**Pre-Script Event:** `create-workflow-plan` (this document)  
**Post-Assignment Events:** `validate-assignment-completion`, `report-progress` (after each assignment)  
**Post-Script Event:** Apply `orchestration:plan-approved` label to the application plan issue  

### High-Level Summary

1. **Initiate the repository** — configure GitHub settings, labels, projects, branch protection
2. **Create the application plan** — analyze plan docs, produce a phased development plan as a GitHub Issue
3. **Create the project structure** — scaffold the actual codebase (Python/uv project)
4. **Create AGENTS.md** — write agent-facing documentation for AI coding assistants
5. **Debrief and document** — capture learnings, deviations, and improvement recommendations
6. **PR approval and merge** — review, approve, and merge the setup PR; clean up branches

---

## 2. Project Context Summary

### Application Overview

**workflow-orchestration-queue** is a headless agentic orchestration platform that transforms GitHub Issues into autonomous "Execution Orders" fulfilled by specialized AI agents. It shifts the AI paradigm from passive co-pilot to an autonomous background production service.

### Key Architectural Concepts

- **Four Pillars:** The Ear (FastAPI webhook receiver), The State (GitHub Issues as queue), The Brain (Sentinel polling orchestrator), The Hands (DevContainer worker)
- **Self-Bootstrapping:** The system is designed to build itself — Phase 1 is manually seeded, then the orchestrator builds Phases 2 and 3 using its own workflows
- **Script-First Integration:** Uses `devcontainer-opencode.sh` as the bridge to the worker, ensuring environment parity with human developers
- **Markdown-as-a-Database:** Task state is stored entirely in GitHub Issues via labels (`agent:queued`, `agent:in-progress`, `agent:success`, `agent:error`, `agent:infra-failure`)

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12+ |
| Web Framework | FastAPI + Uvicorn |
| Data Validation | Pydantic |
| HTTP Client | HTTPX (async) |
| Package Manager | uv (Rust-based) |
| Containerization | Docker / DevContainers |
| Shell Scripts | PowerShell Core (pwsh) / Bash |
| Agent Runtime | opencode CLI (GLM-5) |
| CI/CD | GitHub Actions |

### Project Structure (Planned)

```
/
├── pyproject.toml
├── uv.lock
├── src/
│   ├── notifier_service.py       # FastAPI webhook ingestion
│   ├── orchestrator_sentinel.py  # Background polling & dispatch
│   ├── models/
│   │   └── work_item.py          # Unified WorkItem, TaskType, scrub_secrets()
│   └── queue/
│       └── github_queue.py       # ITaskQueue ABC + GitHubQueue
├── scripts/                      # Shell bridge execution layer
├── local_ai_instruction_modules/ # Markdown logic workflows for LLM
├── docs/                         # Architecture and user documentation
└── tests/                        # Test suite
```

### Key Constraints

- **Action SHA Pinning:** All GitHub Actions workflows MUST pin actions to specific commit SHAs (not version tags)
- **No .NET global.json:** This is a Python/Shell ecosystem — the existing `global.json` in the template is for the template tooling, not the application
- **Simplification decisions already applied:** Several simplifications from the Plan Review have been accepted and incorporated (3 env vars only, hardcoded `"stop"` env reset, single-repo polling, consolidated queue class, no IPv4 scrubbing, stdout-only logging, no `raw_payload` field, no encryption verbiage)
- **Phase 1 scope only:** Current implementation targets the Sentinel MVP (polling, claiming, dispatching). Webhooks (Phase 2) and Deep Orchestration (Phase 3) are deferred to future work

### Repository Details

- **Repo:** `intel-agency/workflow-orchestration-queue-tango74` (template clone)
- **Template:** `workflow-orchestration-queue-tango74` (base template with .NET/Aspire tooling in devcontainer)
- **Branch Strategy:** `main` (stable) + feature branches with PR workflow
- **Existing Template Infrastructure:** DevContainer configs, GitHub Actions workflows (validate, publish-docker, prebuild-devcontainer, orchestrator-agent), opencode agent definitions, shell test suite

### Reference Implementation Files (in plan_docs/)

- `orchestrator_sentinel.py` — Reference implementation of the Sentinel with all Plan Review fixes applied
- `notifier_service.py` — Reference implementation of the FastAPI webhook receiver with env validation
- `src/models/work_item.py` — Unified data model with credential scrubber
- `src/queue/github_queue.py` — Consolidated GitHub queue with connection pooling and assign-then-verify
- `interactive-report.html` — React-based interactive architecture dashboard

### Known Risks

1. **Template mismatch:** The template is a .NET/Aspire-oriented devcontainer, but the application is Python. The project structure must adapt accordingly.
2. **Branch protection PAT requirement:** Importing branch protection rulesets requires `GH_ORCHESTRATION_AGENT_TOKEN` with `administration: write` scope — `GITHUB_TOKEN` from Actions may not suffice.
3. **GitHub Project creation:** Requires `project` and `read:project` scopes; may fail if the token lacks these.
4. **Long execution chain:** Six sequential assignments with post-assignment events means ~18 sub-tasks total. Any failure requires careful rollback.

---

## 3. Assignment Execution Plan

### Assignment 1: `init-existing-repository`

| Field | Content |
|---|---|
| **Assignment** | `init-existing-repository`: Initiate Existing Repository |
| **Goal** | Configure the repository with GitHub settings, labels, projects, branch protection, and renamed files; open a setup PR |
| **Key Acceptance Criteria** | 1. New branch `dynamic-workflow-project-setup` created (all work commits here) 2. Branch protection ruleset imported from `.github/protected-branches_ruleset.json` 3. GitHub Project created with Board columns (Not Started, In Progress, In Review, Done) 4. Labels imported from `.github/.labels.json` 5. Devcontainer and workspace files renamed to match repo name 6. PR created from branch to `main` |
| **Project-Specific Notes** | The repo already has `.github/.labels.json` and `.github/protected-branches_ruleset.json` from the template. The workspace file is already named `workflow-orchestration-queue-tango74.code-workspace`. The devcontainer `name` in `.devcontainer/devcontainer.json` may already match. Verify before renaming. Branch protection import requires `GH_ORCHESTRATION_AGENT_TOKEN` with `administration: write` scope. |
| **Prerequisites** | GitHub authentication with `repo`, `project`, `read:project`, `read:user`, `user:email` scopes. `administration: write` scope for branch protection. |
| **Dependencies** | None (first assignment) |
| **Risks / Challenges** | - Branch protection ruleset import may fail due to token scope limitations. Workaround: skip and document if token lacks `administration: write`.\n- GitHub Project creation may fail if org-level permissions are restricted.\n- The template's existing `global.json` is for .NET — the application doesn't need it, but it shouldn't be removed (it's template infrastructure). |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### Assignment 2: `create-app-plan`

| Field | Content |
|---|---|
| **Assignment** | `create-app-plan`: Create Application Plan |
| **Goal** | Analyze all plan_docs/ documents and produce a comprehensive application plan documented as a GitHub Issue with milestones, linked to the project board |
| **Key Acceptance Criteria** | 1. Application template thoroughly analyzed 2. Plan documented in a GitHub Issue using the template from `.github/ISSUE_TEMPLATE/application-plan.md` 3. Milestones created and linked 4. Issue added to GitHub Project 5. Labels applied (`planning`, `documentation`) 6. No implementation code written — planning only |
| **Project-Specific Notes** | The primary app spec is `OS-APOW Implementation Specification v1.2.md`. Supporting docs: Architecture Guide v3.2, Development Plan v4.2, Plan Review, Simplification Report. Reference implementations exist in `plan_docs/` (sentinel, notifier, queue, models). The plan should reflect the 4-phase roadmap (Phase 0: Seeding, Phase 1: Sentinel MVP, Phase 2: Ear/Webhooks, Phase 3: Deep Orchestration). Phase 3 features and deferred items should be in a "Future Work" appendix per Simplification Report S-9. The `global.json` question in the spec says "No" — the application is Python-based. |
| **Prerequisites** | Assignment 1 complete (GitHub Project exists, labels imported, branch created) |
| **Dependencies** | GitHub Project from Assignment 1, label set from Assignment 1 |
| **Risks / Challenges** | - The plan docs are extensive and contain some duplication (noted in Simplification Report S-2, kept by design). The agent must synthesize, not copy-paste.\n- The `.github/ISSUE_TEMPLATE/application-plan.md` must exist — verify it's in the template.\n- Pre-assignment event `gather-context` and failure event `recover-from-error` add sub-tasks.\n- Must NOT apply `orchestration:plan-approved` label — that's done by the workflow's post-script-complete event. |
| **Events** | Pre-assignment: `gather-context`; Post-assignment: `validate-assignment-completion`, `report-progress`; On-failure: `recover-from-error` |

### Assignment 3: `create-project-structure`

| Field | Content |
|---|---|
| **Assignment** | `create-project-structure`: Create Project Structure |
| **Goal** | Create the actual project scaffolding — Python/uv project files, source directories, Docker configs, CI/CD pipelines, documentation structure, and repository summary |
| **Key Acceptance Criteria** | 1. Solution/project structure created per the app plan's tech stack 2. All project files and directories established 3. Docker and docker-compose configs created 4. Basic CI/CD pipeline established 5. Documentation structure (README, docs/) created 6. Initial commit with complete scaffolding 7. Repository summary (`.ai-repository-summary.md`) created 8. All GitHub Actions pinned to commit SHAs 9. Build validates successfully |
| **Project-Specific Notes** | Tech stack is Python 3.12+ with uv. Use `pyproject.toml` + `uv.lock`. The Implementation Spec defines the exact project structure (see §Project Structure). Reference implementations in `plan_docs/` should guide the actual code but the scaffolding must be production-ready. The existing `scripts/` directory from the template (shell bridge scripts, auth helpers) must be preserved. The `.github/workflows/` directory already has template workflows — the application's CI/CD must integrate with or supplement these. **Do NOT use curl in docker-compose healthchecks** — use Python's stdlib instead. Ensure `COPY src/ ./src/` appears before any `uv pip install -e .` in Dockerfiles. |
| **Prerequisites** | Assignment 2 complete (application plan exists as a GitHub Issue) |
| **Dependencies** | Application plan from Assignment 2, tech stack decisions, architecture decisions |
| **Risks / Challenges** | - The template repo already has .NET-oriented files (`global.json`, .NET SDK in Dockerfile). The Python project must coexist without breaking template infrastructure.\n- Dockerfile for the Python services must be created alongside the existing devcontainer Dockerfile.\n- The existing `.github/workflows/validate.yml` (or equivalent) runs lint/scan/test — new project files must pass these checks.\n- Creating a `.ai-repository-summary.md` requires reading the instructions from the remote `create-repository-summary.md` file. |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### Assignment 4: `create-agents-md-file`

| Field | Content |
|---|---|
| **Assignment** | `create-agents-md-file`: Create AGENTS.md File |
| **Goal** | Create an `AGENTS.md` file at the repository root providing AI coding agents with precise, actionable context about the project |
| **Key Acceptance Criteria** | 1. `AGENTS.md` exists at repository root 2. Contains project overview, setup/build/test commands 3. Commands have been validated by running them 4. Contains code style, project structure, testing instructions 5. Contains PR/commit guidelines 6. File is committed and pushed to working branch |
| **Project-Specific Notes** | An `AGENTS.md` already exists at the root (from the template). The new file must replace/update it with project-specific content. The existing file describes the template repo's orchestration system. The new file should describe the OS-APOW application itself. Key commands to document: `uv sync` (install deps), `uv run pytest` (tests), `uv run python -m src.orchestrator_sentinel` (run sentinel), `uv run uvicorn src.notifier_service:app` (run notifier). Cross-reference with `README.md` and `.ai-repository-summary.md`. |
| **Prerequisites** | Assignments 1-3 complete (project structure exists, build works, tests pass) |
| **Dependencies** | Working build/test commands from Assignment 3, project structure from Assignment 3 |
| **Risks / Challenges** | - If the project doesn't build/test successfully in Assignment 3, the commands listed in AGENTS.md won't validate.\n- Must not duplicate entire README.md sections — complement, don't copy.\n- The existing AGENTS.md has detailed template-specific instructions that are still relevant for the orchestration system. Careful consideration needed on what to keep vs. replace. |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### Assignment 5: `debrief-and-document`

| Field | Content |
|---|---|
| **Assignment** | `debrief-and-document`: Debrief and Document Learnings |
| **Goal** | Perform a comprehensive debriefing capturing key learnings, deviations, errors, and improvement recommendations from the entire workflow execution |
| **Key Acceptance Criteria** | 1. Detailed report with all 12 required sections 2. All deviations from assignments documented 3. Execution trace saved as `debrief-and-document/trace.md` 4. Report reviewed and approved 5. Report committed and pushed |
| **Project-Specific Notes** | The report template requires specific sections: Executive Summary, Workflow Overview, Key Deliverables, Lessons Learned, What Worked Well, What Could Be Improved, Errors Encountered, Complex Steps, Suggested Changes, Metrics, Future Recommendations, Conclusion. This is meta-work — documenting the process of setting up the project. Must flag any plan-impacting findings as ACTION ITEMS. |
| **Prerequisites** | Assignments 1-4 complete |
| **Dependencies** | Full execution history of all prior assignments |
| **Risks / Challenges** | - This assignment requires thorough recall of all prior steps. The agent must maintain a detailed execution trace from the beginning.\n- The "Suggested Changes" section should feed back into the workflow assignment files in `agent-instructions` — this is valuable for continuous improvement. |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

### Assignment 6: `pr-approval-and-merge`

| Field | Content |
|---|---|
| **Assignment** | `pr-approval-and-merge`: Pull Request Approval and Merge |
| **Goal** | Complete the full PR approval and merge process for the setup PR, including CI verification, code review, comment resolution, merge, and cleanup |
| **Key Acceptance Criteria** | 1. All CI/CD checks pass (CI remediation loop up to 3 attempts) 2. Code review delegated to `code-reviewer` subagent 3. All review comments resolved via `ai-pr-comment-protocol.md` 4. PR merged to `main` 5. Source branch deleted 6. Related issues closed 7. Run report with evidence artifacts produced |
| **Project-Specific Notes** | This is an automated setup PR — self-approval by the orchestrator is acceptable per the workflow spec. The `$pr_num` comes from Assignment 1 output (`#initiate-new-repository.init-existing-repository`). The CI remediation loop (Phase 0.5) MUST be executed. After merge: delete the setup branch and close related setup issues. The PR contains all work from Assignments 1-5. |
| **Prerequisites** | All prior assignments complete, PR number from Assignment 1 |
| **Dependencies** | PR exists (from Assignment 1), all code committed (from Assignments 2-5) |
| **Risks / Challenges** | - CI may fail on new project files (linting, type checking, tests). Up to 3 fix cycles allowed.\n- If `code-reviewer` subagent or auto-reviewers (Copilot, CodeQL) find issues, they must be resolved before merge.\n- Merge conflicts unlikely since it's a feature branch, but possible if `main` receives other commits.\n- **CRITICAL:** All local changes MUST be committed and pushed BEFORE merge. |
| **Events** | Post-assignment: `validate-assignment-completion`, `report-progress` |

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PRE-SCRIPT-BEGIN EVENT                                                  │
│ └─ create-workflow-plan  ◄── (THIS DOCUMENT)                            │
│     └─ Output: plan_docs/workflow-plan.md                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ASSIGNMENT 1: init-existing-repository                                  │
│ └─ Create branch: dynamic-workflow-project-setup                        │
│ └─ Import branch protection ruleset                                     │
│ └─ Create GitHub Project + columns                                      │
│ └─ Import labels                                                        │
│ └─ Rename workspace/devcontainer files                                  │
│ └─ Create setup PR → $pr_num                                            │
│ └─ Post: validate-assignment-completion, report-progress                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ASSIGNMENT 2: create-app-plan                                           │
│ ├─ Pre: gather-context                                                  │
│ └─ Analyze plan_docs/ (all 9 files + src/)                              │
│ └─ Create tech-stack.md, architecture.md in plan_docs/                  │
│ └─ Create GitHub Issue (application plan) → $plan_issue                 │
│ └─ Create milestones, link issue to project                             │
│ └─ Post: validate-assignment-completion, report-progress                │
│ └─ On-failure: recover-from-error                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ASSIGNMENT 3: create-project-structure                                  │
│ └─ Create pyproject.toml, src/ directory structure                      │
│ └─ Create Dockerfile, docker-compose.yml                                │
│ └─ Create CI/CD workflows (SHA-pinned actions)                          │
│ └─ Create README.md, docs/ structure                                    │
│ └─ Create .ai-repository-summary.md                                     │
│ └─ Validate build                                                       │
│ └─ Post: validate-assignment-completion, report-progress                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ASSIGNMENT 4: create-agents-md-file                                     │
│ └─ Validate build/test commands                                         │
│ └─ Write AGENTS.md (project overview, commands, structure, style)       │
│ └─ Cross-reference with README.md, .ai-repository-summary.md           │
│ └─ Post: validate-assignment-completion, report-progress                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ASSIGNMENT 5: debrief-and-document                                      │
│ └─ Create debrief report (12 sections)                                  │
│ └─ Save execution trace: debrief-and-document/trace.md                  │
│ └─ Post: validate-assignment-completion, report-progress                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ASSIGNMENT 6: pr-approval-and-merge                                     │
│ └─ CI verification & remediation loop (up to 3 attempts)                │
│ └─ Code review delegation (code-reviewer subagent)                      │
│ └─ Resolve all review comments (ai-pr-comment-protocol.md)              │
│ └─ Merge PR to main                                                     │
│ └─ Delete source branch, close related issues                           │
│ └─ Post: validate-assignment-completion, report-progress                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ POST-SCRIPT-COMPLETE EVENT                                              │
│ └─ Apply `orchestration:plan-approved` label to $plan_issue             │
│     (signals next phase of orchestration pipeline)                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Open Questions

### Q1: Branch Protection Token Scope

The `init-existing-repository` assignment requires importing a branch protection ruleset via `gh api`. The assignment specifies using `GH_ORCHESTRATION_AGENT_TOKEN` (a PAT) rather than `GITHUB_TOKEN`. Does the current environment have this token available, and does it have `administration: write` scope?

**Impact:** If unavailable, the branch protection import step will be skipped with a documented error. This is non-blocking for the rest of the workflow.

### Q2: GitHub Project Creation Permissions

Creating a GitHub Project and linking it to the repository requires `project` and `read:project` scopes on the token. Have these been verified?

**Impact:** If the token lacks these scopes, the project creation step will fail. The `scripts/test-github-permissions.ps1` script can verify this.

### Q3: `.github/ISSUE_TEMPLATE/application-plan.md` Existence

The `create-app-plan` assignment references a template at `.github/ISSUE_TEMPLATE/application-plan.md`. Does this file exist in the template repository? If not, the agent will need to create it or use an alternative format.

**Impact:** Medium — affects the structure of the application plan issue.

### Q4: Coexistence of Python Application with .NET Template Infrastructure

The template repo has .NET-oriented infrastructure (`global.json`, .NET SDK in Dockerfile, .NET-related scripts). The application is Python-based. How should these coexist? Should the .NET infrastructure be preserved (for the orchestration tooling that uses the template), or should it be replaced?

**Impact:** High — affects the entire project structure. Current recommendation: preserve template infrastructure and add Python project alongside it.

### Q5: AGENTS.md — Replace or Merge?

An `AGENTS.md` already exists at the root with template-specific instructions for the orchestration system. The `create-agents-md-file` assignment wants to create a new one for the OS-APOW application. Should the existing template instructions be preserved in a separate section, or replaced entirely?

**Impact:** Medium — affects developer/agent experience. Current recommendation: replace with project-specific content but preserve a reference section for the template orchestration system.

### Q6: Cost Guardrails and Deferred Features

Several features from the plan are explicitly deferred (cost guardrails, cross-repo polling, self-healing reconciliation loop, architect sub-agent). Should the application plan issue track these as separate future milestones, or as items within existing milestones?

**Impact:** Low — affects milestone granularity. Recommendation: include in a "Future Work" appendix per Simplification Report S-9, with separate milestone tracking deferred until those phases are scoped.

---

## Appendix A: plan_docs/ Files Inventory

| File | Description | Status |
|------|-------------|--------|
| `OS-APOW Implementation Specification v1.2.md` | Primary app spec — features, requirements, tech stack, project structure, acceptance criteria | Read |
| `OS-APOW Architecture Guide v3.2.md` | System architecture — 4 pillars, ADRs, data flow, security model, self-bootstrapping lifecycle | Read |
| `OS-APOW Development Plan v4.2.md` | Phased roadmap — motivation, user stories per phase, risk assessment, cross-cutting directions | Read |
| `OS-APOW Plan Review.md` | Code review of plan docs — strengths (S-1..S-7), issues (I-1..I-10), recommendations (R-1..R-9) | Read |
| `OS-APOW Simplification Report v1.md` | Simplification opportunities (S-1..S-11) with status (IMPLEMENTED/KEPT) and user decisions | Read |
| `orchestrator_sentinel.py` | Reference Sentinel implementation with all Plan Review fixes (heartbeat, locking, backoff, signals) | Read |
| `notifier_service.py` | Reference FastAPI notifier with env validation, HMAC verification, shared model imports | Read |
| `interactive-report.html` | React-based interactive architecture dashboard (Tailwind CSS, Lucide icons) | Read |
| `src/models/work_item.py` | Unified WorkItem model, TaskType enum, WorkItemStatus enum, scrub_secrets() | Read |
| `src/queue/github_queue.py` | ITaskQueue ABC, GitHubQueue with connection pooling, claim_task with assign-then-verify | Read |
| `src/__init__.py` | Empty package init | Read |
| `src/models/__init__.py` | Re-exports TaskType, WorkItemStatus, WorkItem, scrub_secrets | Read |
| `src/queue/__init__.py` | Empty package init | Read |

---

## Appendix B: Event Assignments

### Pre-Script-Begin Events
- `create-workflow-plan` → This document

### Post-Assignment-Complete Events (after each of the 6 assignments)
- `validate-assignment-completion` — Verify the assignment met all acceptance criteria
- `report-progress` — Report current workflow progress to stakeholders

### Post-Script-Complete Events
- Apply `orchestration:plan-approved` label to the application plan issue (from Assignment 2)

### Assignment-Specific Events (create-app-plan only)
- Pre-assignment: `gather-context`
- On-failure: `recover-from-error`
