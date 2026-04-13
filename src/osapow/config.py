"""Application configuration via Pydantic Settings.

Loads and validates all required environment variables at startup.
Crashes immediately with a clear error if any required variable is missing
or set to a placeholder value.

Required environment variables (per Simplification Report S-3):
- GITHUB_TOKEN: GitHub App installation token for API access
- GITHUB_ORG: GitHub organization/owner name
- GITHUB_REPO: Target repository name

Optional environment variables:
- WEBHOOK_SECRET: HMAC secret for webhook signature verification (Notifier only)
- SENTINEL_BOT_LOGIN: Bot account login for assign-then-verify locking
- POLL_INTERVAL: Seconds between Sentinel poll cycles (default: 60)
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All secrets are loaded exclusively from environment variables.
    Never hardcode secrets or embed defaults for sensitive values.
    """

    # Required — shared
    github_token: str
    github_org: str
    github_repo: str

    # Required — Notifier
    webhook_secret: str = ""

    # Optional — Sentinel
    sentinel_bot_login: str = ""
    poll_interval: int = 60

    model_config = {"env_prefix": "", "case_sensitive": False}
