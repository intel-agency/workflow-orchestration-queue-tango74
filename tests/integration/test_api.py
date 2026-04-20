"""Integration tests for OS-APOW API endpoints."""



class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check(self, client):
        """Verify health check returns expected payload."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["system"] == "OS-APOW Notifier"


class TestWebhookEndpoint:
    """Tests for the /webhooks/github endpoint."""

    def test_webhook_accepts_post(self, client):
        """Verify webhook endpoint accepts POST requests."""
        response = client.post(
            "/webhooks/github",
            json={"action": "opened"},
            headers={"X-Hub-Signature-256": "sha256=fakesig"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
