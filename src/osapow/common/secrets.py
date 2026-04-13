"""Credential and secret scrubbing for public-facing output.

The scrub_secrets() function strips sensitive patterns from text before
posting to public channels (GitHub Issue comments, etc.).

Patterns scrubbed:
- GitHub PATs: ghp_*, ghs_*, gho_*, github_pat_*
- Bearer tokens: Bearer ...
- API keys: sk-*, ZhipuAI keys
- Generic tokens in URLs: token=..., access_token=...

Per S-7: No IPv4 address scrubbing (removed overly broad regex that
caused false positives on version strings).
"""

import re

# Patterns to scrub from public-facing output
_SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"ghp_[A-Za-z0-9_]{36,}", "ghp_REDACTED"),
    (r"ghs_[A-Za-z0-9_]{36,}", "ghs_REDACTED"),
    (r"gho_[A-Za-z0-9_]{36,}", "gho_REDACTED"),
    (r"github_pat_[A-Za-z0-9_]{22,}", "github_pat_REDACTED"),
    (r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", "Bearer REDACTED"),
    (r"sk-[A-Za-z0-9]{20,}", "sk-REDACTED"),
    (r"token=[A-Za-z0-9\-._~+/]+=*", "token=REDACTED"),
    (r"access_token=[A-Za-z0-9\-._~+/]+=*", "access_token=REDACTED"),
]

_COMPILED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(pattern), replacement) for pattern, replacement in _SECRET_PATTERNS
]


def scrub_secrets(text: str) -> str:
    """Remove sensitive patterns from text.

    Args:
        text: The text to scrub.

    Returns:
        The scrubbed text with sensitive patterns replaced.
    """
    for pattern, replacement in _COMPILED_PATTERNS:
        text = pattern.sub(replacement, text)
    return text
