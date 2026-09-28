# -*- coding: utf-8 -*-
"""Reddit — multi-backend: OpenCLI / rdt-cli. Login is mandatory.

Honest tiering (live-verified 2026-06): there is NO zero-config path.
Anonymous .json endpoints are blocked (403 anti-bot, all variants), and
the official API closed self-service registration in 2025-11 (manual
approval, individual scripts rarely granted — PRAW is only an option for
users who already hold credentials). Every working backend rides a
logged-in session: OpenCLI reuses the browser's, rdt-cli imports cookies.
"""

import json
import shutil
import time
from pathlib import Path

from deep_scrape.utils.paths import (
    PrivatePathError,
    home_dir,
    read_small_text_no_follow,
)

from .base import Channel

_CREDENTIAL_FILE = "~/.config/rdt-cli/credential.json"
_CREDENTIAL_TTL_SECONDS = 7 * 86400
_MAX_CREDENTIAL_BYTES = 1024 * 1024
# Pinned to the 0.4.2 state — PyPI still only has 0.4.1 (upstream issue #10).
_RDT_GIT_SOURCE = "git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66"


class RedditChannel(Channel):
    name = "reddit"
    description = "Reddit Posts and Comments"
    backends = ["OpenCLI", "rdt-cli"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        from deep_scrape.utils.url import host_matches

        return host_matches(url, "reddit.com", "redd.it")

    def check(self, config=None):
        """Probe candidates in order; first fully-usable backend wins."""
        self.active_backend = None
        findings = []

        for backend in self.ordered_backends(config):
            if backend == "OpenCLI":
                result = self._check_opencli()
            else:
                result = self._check_rdt()
            if result is None:
                continue
            findings.append((backend, *result))

        for wanted in ("ok", "warn"):
            for backend, status, message in findings:
                if status == wanted:
                    self.active_backend = backend if status == "ok" else None
                    return status, message

        if findings:
            return "error", "\n".join(m for _, _, m in findings)

        return "off", (
            "No Reddit backend installed. Note: Reddit has no zero-config path "
            "(anonymous .json blocked, API requires approval); logged-in session required. Recommendations:\n"
            "  Desktop: deepscrape install --system --channels opencli\n"
            "           (reuses Chrome session, active once logged into reddit.com)\n"
            f"  Server/CLI: pipx install '{_RDT_GIT_SOURCE}'\n"
            "           then run `rdt login` or configure cookies manually (see doctor hints)"
        )

    def _check_opencli(self):
        """OpenCLI candidate. None = not installed."""
        from deep_scrape.backends import opencli_status

        st = opencli_status()
        if not st.installed:
            return None
        if st.broken:
            return "error", st.hint
        if st.ready:
            return "warn", (
                "OpenCLI bridge connected, but Reddit login session and live commands are not verified; "
                "Doctor does not execute platform commands to avoid side effects."
            )
        return "warn", st.hint

    def _check_rdt(self):
        """Inspect rdt's saved credential without invoking its auto-refresh."""
        if not shutil.which("rdt"):
            return None

        credential_path = home_dir() / ".config" / "rdt-cli" / "credential.json"
        try:
            payload = read_small_text_no_follow(
                credential_path,
                max_bytes=_MAX_CREDENTIAL_BYTES,
            )
        except PrivatePathError as exc:
            return "warn", (
                f"rdt-cli installed, but credential.json cannot be safely read: {exc}."
            )
        except OSError:
            return "warn", (
                "rdt-cli installed, but credential.json cannot be safely read; "
                "Doctor does not run `rdt status` which auto-refreshes cookies."
            )
        if payload is None:
            return "warn", self._rdt_login_hint()
        try:
            data = json.loads(payload)
        except (UnicodeError, json.JSONDecodeError, ValueError):
            return "warn", (
                "rdt-cli installed, but saved credential.json cannot be safely parsed; "
                "Doctor does not run `rdt status`."
            )
        if not isinstance(data, dict):
            return "warn", self._rdt_login_hint()
        cookies = data.get("cookies")
        if not isinstance(cookies, dict) or not cookies.get("reddit_session"):
            return "warn", self._rdt_login_hint()

        saved_at = data.get("saved_at")
        if isinstance(saved_at, (int, float)) and (
            time.time() - saved_at > _CREDENTIAL_TTL_SECONDS
        ):
            return "warn", (
                "rdt-cli installed; saved cookies are older than 7 days. Doctor will not auto-refresh; "
                "please update explicitly using Cookie-Editor."
            )
        return "warn", (
            "rdt-cli installed with explicit saved Reddit cookies; Doctor does not run `rdt status` "
            "to prevent unauthorized browser cookie rewrites."
        )

    @staticmethod
    def _rdt_login_hint():
        return (
            "rdt-cli installed but no valid explicit cookie found. Use Cookie-Editor:\n"
            "  1. Install Cookie-Editor extension in Chrome:\n"
            "     https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm\n"
            "  2. Open reddit.com (ensure logged in)\n"
            "  3. Click Cookie-Editor icon, find `reddit_session`, copy its Value\n"
            f"  4. Write to {_CREDENTIAL_FILE}:\n"
            '     {"cookies": {"reddit_session": "<value>"}, '
            '"source": "manual", "username": "<username>", '
            '"modhash": null, "saved_at": 0, "last_verified_at": null}\n\n'
            "Doctor will not run `rdt status` to prevent automatic browser reads."
        )
