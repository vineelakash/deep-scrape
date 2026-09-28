# -*- coding: utf-8 -*-
"""Twitter/X — check if twitter-cli or bird CLI is available."""

import os
import shutil

from deep_scrape.utils.url import host_matches

from .base import Channel


def twitter_cli_child_env(config=None) -> dict[str, str]:
    """Return dictionary with twitter environment variables."""
    child_env = {}
    for env_name, config_key in (
        ("TWITTER_AUTH_TOKEN", "twitter_auth_token"),
        ("TWITTER_CT0", "twitter_ct0"),
    ):
        if env_name in os.environ:
            child_env[env_name] = os.environ[env_name]
        elif config is not None:
            value = config.get(config_key)
            if value:
                child_env[env_name] = str(value)
    return child_env


class TwitterChannel(Channel):
    name = "twitter"
    description = "Twitter/X Tweets and Threads"
    backends = ["twitter-cli", "OpenCLI", "bird CLI (legacy)"]
    tier = 1
    _child_env = staticmethod(twitter_cli_child_env)

    def can_handle(self, url: str) -> bool:
        return host_matches(url, "x.com", "twitter.com")

    def check(self, config=None):
        """Probe candidates in order; first fully-usable backend wins."""
        self.active_backend = None
        findings = []

        for backend in self.ordered_backends(config):
            if backend == "twitter-cli":
                result = self._check_twitter_cli(config)
            elif backend == "OpenCLI":
                result = self._check_opencli()
            elif backend == "bird CLI (legacy)":
                result = self._check_bird()
            else:
                continue

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

        return "warn", (
            "Twitter CLI not installed. Installation options:\n"
            "  pipx install twitter-cli\n"
            "or:\n"
            "  uv tool install twitter-cli"
        )

    def _check_twitter_cli(self, config=None):
        """Inspect explicit credentials without starting twitter-cli."""
        if not shutil.which("twitter"):
            return None

        child_env = twitter_cli_child_env(config)
        auth_token = os.environ.get("TWITTER_AUTH_TOKEN") or child_env.get(
            "TWITTER_AUTH_TOKEN"
        )
        ct0 = os.environ.get("TWITTER_CT0") or child_env.get("TWITTER_CT0")
        if auth_token and ct0:
            return "warn", (
                "twitter-cli installed and credentials configured; Doctor does not run `twitter status` "
                "to avoid automatic browser cookie fallback. Manually verify when desired."
            )
        return "warn", (
            "twitter-cli installed without explicit credentials. Export from x.com using Cookie-Editor:\n"
            "  deepscrape configure twitter-cookies\n"
            "Doctor will not automatically read browser cookies."
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
                "OpenCLI bridge connected, but Twitter/X login session and live commands are not verified; "
                "Doctor does not execute platform commands to avoid side effects."
            )
        return "warn", st.hint

    def _check_bird(self):
        """Inspect legacy bird credentials without launching browser fallback."""
        for cmd in ("bird", "birdx"):
            if not shutil.which(cmd):
                continue
            if os.environ.get("AUTH_TOKEN") and os.environ.get("CT0"):
                return (
                    "warn",
                    f"{cmd} installed with explicit environment credentials; Doctor skips `check` "
                    "to prevent browser fallback.",
                )
            return "warn", (
                f"{cmd} installed without explicit AUTH_TOKEN/CT0; "
                "use manually exported Cookie-Editor credentials only."
            )
        return None
