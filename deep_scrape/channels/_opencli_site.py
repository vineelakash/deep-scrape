# -*- coding: utf-8 -*-
"""Shared channel helper for OpenCLI browser-session-only platforms."""

from deep_scrape.utils.url import host_matches

from .base import Channel


class OpenCLISiteChannel(Channel):
    """A platform served directly by OpenCLI.

    These channels are intentionally thin: DeepScrape installs,
    health-checks, and routes. Agents call `opencli <site> ...` directly.
    """

    site: str = ""
    domains: tuple[str, ...] = ()
    usage: str = ""
    login_hint: str = ""

    backends = ["OpenCLI"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        return host_matches(url, *self.domains)

    def check(self, config=None):
        from deep_scrape.backends import opencli_status

        self.active_backend = None
        st = opencli_status()
        if not st.installed:
            return "off", (
                f"No backend installed for {self.description}. Install:\\n"
                "  deepscrape install --system --channels opencli\\n"
                f"Then log into {self.login_hint} in Chrome"
            )
        if st.broken:
            return "error", st.hint

        if st.ready:
            return "warn", (
                f"OpenCLI bridge connected, but {self.description} login session and live commands "
                "are not verified; Doctor does not execute platform commands to avoid side effects. "
                f"When needed, ensure you are logged into {self.login_hint} in Chrome."
            )
        return "warn", st.hint
