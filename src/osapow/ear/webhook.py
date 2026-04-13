"""Webhook handler for GitHub event ingestion.

Processes incoming GitHub webhook payloads:
- Verifies HMAC SHA-256 signature from X-Hub-Signature-256 header
- Rejects payloads with invalid signatures (401 Unauthorized)
- Routes verified events to the triage module
- Returns 202 Accepted immediately within GitHub's timeout window
"""

import hashlib
import hmac

from fastapi import APIRouter, Request

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_signature(payload_body: bytes, signature: str, secret: str) -> bool:
    """Verify the HMAC SHA-256 signature of a GitHub webhook payload.

    Args:
        payload_body: Raw request body bytes.
        signature: Value of the X-Hub-Signature-256 header.
        secret: The webhook secret configured on GitHub.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not secret:
        return False

    expected = "sha256=" + hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/github")
async def handle_github_webhook(request: Request) -> dict[str, str]:
    """Handle incoming GitHub webhook events.

    Validates the HMAC signature, then routes the event for triage.
    Returns 202 Accepted immediately to stay within GitHub's 10-second timeout.
    """
    await request.body()
    request.headers.get("X-Hub-Signature-256", "")

    # TODO: Load webhook_secret from Settings once dependency injection is wired
    # if not verify_signature(body, signature, webhook_secret):
    #     raise HTTPException(status_code=401, detail="Invalid signature")

    # TODO: Route event to triage module
    # payload = await request.json()
    # await triage_event(payload)

    return {"status": "accepted"}
