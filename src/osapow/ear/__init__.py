"""Ear (Listener) service — webhook intake and event triage.

The Ear is the system's sensory input layer. It:
- Receives GitHub webhook events via POST /webhooks/github
- Verifies HMAC SHA-256 signatures (rejects unauthorized with 401)
- Parses event payloads to detect task templates
- Applies agent:queued labels via GitHub API
- Returns 202 Accepted within GitHub's 10-second timeout
"""
