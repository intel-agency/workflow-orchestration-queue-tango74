"""Hands (Executor) service — shell-bridge execution in isolated environments.

The Hands pillar provides the isolated execution environment where actual
coding happens. Key characteristics:
- High-fidelity DevContainer — identical to human developer environments
- Segregated Docker bridge network — no access to host subnets
- Resource constraints: 2 CPUs, 4GB RAM hard limit
- Ephemeral credentials — injected, never written to disk
- Logic-as-Markdown — reads instruction modules for behavior
"""
