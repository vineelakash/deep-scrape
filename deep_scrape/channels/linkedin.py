# -*- coding: utf-8 -*-
"""LinkedIn — check if mcp-server-linkedin is configured."""

import shutil

from .base import Channel
from .mcporter import McporterConfigError, inspect_mcporter_config

_LINKEDIN_SERVER_NAMES = {
    "linkedin",
    "linkedin-scraper",
    "linkedin-scraper-mcp",
    "mcp-server-linkedin",
}
_LOGIN_COMMAND = "uvx mcp-server-linkedin@latest --login"
_UV_INSTALL_URL = "https://docs.astral.sh/uv/getting-started/installation/"
_CONFIG_COMMAND = (
    "mcporter config add linkedin --command uvx "
    "--arg mcp-server-linkedin@latest --env UV_HTTP_TIMEOUT=300 --scope home"
)


class LinkedInChannel(Channel):
    name = "linkedin"
    description = "LinkedIn Professional Network"
    backends = ["mcp-server-linkedin", "Jina Reader"]
    tier = 2

    def can_handle(self, url: str) -> bool:
        from deep_scrape.utils.url import host_matches

        return host_matches(url, "linkedin.com")

    def check(self, config=None):
        self.active_backend = None
        if not shutil.which("mcporter"):
            return "off", (
                "Basic public pages can be read via Jina Reader. Full functionality requires:\n"
                f"  1. Install uv/uvx: {_UV_INSTALL_URL}\n"
                f"  2. {_LOGIN_COMMAND}\n"
                f"  3. {_CONFIG_COMMAND}\n"
                "  See details at https://github.com/stickerdaniel/linkedin-mcp-server"
            )
        try:
            inspection = inspect_mcporter_config()
        except McporterConfigError as exc:
            return "error", f"mcporter configuration check failed: {exc}"
        if inspection.server_names & _LINKEDIN_SERVER_NAMES:
            if not shutil.which("uvx"):
                return "warn", (
                    "LinkedIn MCP is registered in mcporter config, but uvx is not installed; "
                    "cannot launch service. Install:\n"
                    f"  {_UV_INSTALL_URL}"
                )
            return "warn", (
                "LinkedIn MCP is registered in mcporter config; Doctor does not start local "
                "services for connectivity tests to avoid side effects."
            )
        if inspection.imports_unchecked:
            return "warn", (
                "mcporter local configuration did not define LinkedIn MCP; editor imports are active but unchecked."
            )
        return "off", (
            "mcporter is installed but LinkedIn MCP is not configured. Run:\n"
            f"  1. Install uv/uvx: {_UV_INSTALL_URL}\n"
            f"  2. {_LOGIN_COMMAND}\n"
            f"  3. {_CONFIG_COMMAND}"
        )
