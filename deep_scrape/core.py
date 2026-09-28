# -*- coding: utf-8 -*-
"""
DeepScrape — Autonomous Web & Multi-Platform Intelligence Engine.

DeepScrape empowers AI agents to search, read, and extract data across
the internet (LinkedIn, Twitter/X, Reddit, Exa Neural Search, YouTube,
GitHub, Web Reader, RSS, etc.).

Usage:
    from deep_scrape.doctor import check_all, format_report
    from deep_scrape.config import Config

    config = Config()
    results = check_all(config)
    print(format_report(results))
"""

from typing import Dict, Optional

from deep_scrape.config import Config


class DeepScrape:
    """Autonomous Web & Multi-Platform Intelligence Engine.

    Provides platform diagnostics, health checking, and configuration.
    For searching and deep-scraping, agents call the platform backends directly
    or use the CLI (see SKILL.md for command patterns).
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()

    def doctor(self) -> Dict[str, dict]:
        """Check availability across all configured channels."""
        from deep_scrape.doctor import check_all
        return check_all(self.config)

    def doctor_report(self) -> str:
        """Get formatted diagnostic health report."""
        from deep_scrape.doctor import check_all, format_report
        return format_report(check_all(self.config))


# Backwards compatibility alias
AgentReach = DeepScrape

