# OS-APOW Architecture

This document links to the canonical architecture specification.

For the complete architecture document, see [plan_docs/architecture.md](../plan_docs/architecture.md).

## Overview

OS-APOW (Orchestration System - Automated Pipeline Orchestration Workflow) is a
headless agentic orchestration platform built on four pillars:

| Pillar | Name         | Responsibility                                    |
|--------|-------------|---------------------------------------------------|
| Ear    | Listener     | Webhook intake and event triage                    |
| State  | Queue        | Task management via GitHub Issues                  |
| Brain  | Orchestrator | Task decomposition and agent coordination          |
| Hands  | Executor     | Shell-bridge execution in isolated DevContainers   |

For the technology stack, see [plan_docs/tech-stack.md](../plan_docs/tech-stack.md).
