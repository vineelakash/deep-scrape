# -*- coding: utf-8 -*-
"""YouTube — check if yt-dlp is available and verify JS runtime configuration."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from deep_scrape.probe import probe_command
from deep_scrape.utils.paths import (
    PrivatePathError,
    get_ytdlp_config_path,
    read_small_text_no_follow,
    render_ytdlp_fix_command,
)

from .base import Channel

_YTDLP_UPGRADE_COMMAND = 'python -m pip install -U "yt-dlp[default]"'
_MAX_CONFIG_BYTES = 1024 * 1024
_JS_RUNTIMES_SUPPORTED_FROM = (2025, 11, 12)


def _parse_ytdlp_version(raw: str) -> tuple[int, ...] | None:
    match = re.search(r"\b(\d{4})\.(\d{1,2})\.(\d{1,2})(?:\.(\d+))?\b", raw)
    if not match:
        return None
    return tuple(int(group) for group in match.groups() if group is not None)


def _has_js_runtime_config(config_path: Path) -> bool:
    try:
        content = read_small_text_no_follow(
            config_path,
            max_bytes=_MAX_CONFIG_BYTES,
        )
        return bool(content and "--js-runtimes" in content)
    except (OSError, UnicodeError, PrivatePathError):
        return False


class YouTubeChannel(Channel):
    name = "youtube"
    description = "YouTube Videos and Subtitles"
    backends = ["yt-dlp"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        from deep_scrape.utils.url import host_matches

        return host_matches(url, "youtube.com", "youtu.be")

    def check(self, config=None):
        probe = probe_command("yt-dlp", ["--version"], timeout=10, package="yt-dlp")
        if probe.status == "missing":
            self.active_backend = None
            return "off", f"yt-dlp not installed. Install: {_YTDLP_UPGRADE_COMMAND}"
        if probe.status == "broken":
            self.active_backend = None
            return "error", (
                "yt-dlp is installed but cannot execute. Reinstall (with JS support):\n"
                f"  {_YTDLP_UPGRADE_COMMAND}\n{probe.hint}"
            )
        if not probe.ok:
            self.active_backend = None
            detail = probe.hint or probe.output or probe.status
            return "error", f"yt-dlp failed to run normally: {detail}"

        self.active_backend = "yt-dlp"

        # Check JS runtime
        has_js = shutil.which("deno") or shutil.which("node")
        if not has_js:
            return "warn", (
                "yt-dlp is installed but lacks a JS runtime (required by YouTube).\n"
                "  Install Node.js or Deno, then run: deepscrape install --system"
            )

        has_deno = shutil.which("deno")
        if not has_deno:
            ytdlp_config = get_ytdlp_config_path()
            if not _has_js_runtime_config(ytdlp_config):
                version = _parse_ytdlp_version(probe.output)
                if version is None:
                    return "warn", (
                        "Unable to verify whether yt-dlp version supports JS runtime configuration. "
                        "Please upgrade and rerun doctor:\n"
                        f"  {_YTDLP_UPGRADE_COMMAND}"
                    )
                if version < _JS_RUNTIMES_SUPPORTED_FROM:
                    return "warn", (
                        "yt-dlp version is too old to support JS runtime configuration. Please upgrade:\n"
                        f"  {_YTDLP_UPGRADE_COMMAND}"
                    )
                fix_cmd = render_ytdlp_fix_command()
                return "warn", (
                    f"yt-dlp is installed but JS runtime is unconfigured (--js-runtimes node). Run:\n{fix_cmd}"
                )

        msg = "Can extract video metadata and subtitles"
        if config is not None:
            providers = []
            if config.is_configured("groq_whisper"):
                providers.append("groq")
            if config.is_configured("openai_whisper"):
                providers.append("openai")
            if providers:
                missing_media_tools = [
                    tool
                    for tool in ("ffmpeg", "ffprobe")
                    if not shutil.which(tool)
                ]
                if missing_media_tools:
                    msg += (
                        " (audio transcription requires "
                        + ", ".join(missing_media_tools)
                        + ")"
                    )
                else:
                    msg += f", audio transcription available ({'/'.join(providers)})"
        return "ok", msg

    def transcribe(
        self,
        url: str,
        config=None,
        provider: str | None = None,
        allow_provider_fallback: bool = True,
    ) -> str:
        from deep_scrape.transcribe import transcribe

        return transcribe(
            url,
            config=config,
            provider=provider,
            allow_provider_fallback=allow_provider_fallback,
        )
