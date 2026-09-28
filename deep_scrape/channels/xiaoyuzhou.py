# -*- coding: utf-8 -*-
"""Xiaoyuzhou Podcast — transcribe podcasts via Groq Whisper API."""

import os

from deep_scrape.config import Config
from deep_scrape.probe import probe_command

from .base import Channel


class XiaoyuzhouChannel(Channel):
    name = "xiaoyuzhou"
    description = "Xiaoyuzhou Podcasts Transcription"
    backends = ["groq-whisper", "ffmpeg"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        from deep_scrape.utils.url import host_matches

        return host_matches(url, "xiaoyuzhoufm.com")

    def check(self, config=None):
        self.active_backend = None

        probe = probe_command("ffmpeg", ["-version"], timeout=10, package="ffmpeg")
        if probe.status == "missing":
            return "off", (
                "Requires ffmpeg (audio transcoding and chunking). Install:\n"
                "  Ubuntu/Debian: apt install -y ffmpeg\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: winget install Gyan.FFmpeg"
            )
        if not probe.ok:
            return "error", (
                "ffmpeg cannot execute. Reinstall: brew install ffmpeg (macOS) / apt install ffmpeg (Linux)"
            )

        script = os.path.expanduser("~/.deep-scrape/tools/xiaoyuzhou/transcribe.sh")
        if not os.path.isfile(script):
            return "off", (
                "Transcription script not installed. Run:\n"
                "  deepscrape install --env=auto --system --channels=xiaoyuzhou\n"
                "  or copy transcribe.sh to ~/.deep-scrape/tools/xiaoyuzhou/"
            )

        has_key = bool(os.environ.get("GROQ_API_KEY"))
        if not has_key:
            try:
                cfg = config if config is not None else Config()
                has_key = bool(cfg.get("groq_api_key"))
            except Exception:
                has_key = False
        if not has_key:
            return "warn", (
                "Requires Groq API Key (free tier). Steps:\n"
                "  1. Register at https://console.groq.com\n"
                "  2. Run: deepscrape configure groq-key"
            )

        self.active_backend = "groq-whisper"
        return "ok", "Fully available (podcast download + Whisper transcription)"
