# -*- coding: utf-8 -*-
"""XiaoHongShu (RED) — multi-backend: OpenCLI / xiaohongshu-mcp / xhs-cli."""

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
from .mcporter import McporterConfigError, inspect_mcporter_config

_MCP_ENDPOINT = "http://localhost:18060/mcp"
_MCP_INSTALL_URL = "https://github.com/xpzouying/xiaohongshu-mcp"
_MAX_XHS_COOKIE_BYTES = 1024 * 1024
_XHS_COOKIE_TTL_SECONDS = 7 * 86400


def _mcp_service_reachable() -> bool:
    """Return True if xiaohongshu-mcp server is responding on localhost."""
    import urllib.request
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(_MCP_ENDPOINT, timeout=3) as resp:
            return resp.status in (200, 404, 405)
    except Exception:
        return False


def _format_single_note(note: dict) -> dict:
    if not isinstance(note, dict) or not note:
        return note
    res = {}
    for k in ("id", "title", "desc", "type"):
        if k in note:
            res[k] = note[k]
    if "user" in note and isinstance(note["user"], dict):
        res["user"] = {
            "nickname": note["user"].get("nickname", ""),
            "user_id": note["user"].get("user_id", ""),
        }
    interact = note.get("interact_info")
    if isinstance(interact, dict):
        for k in ("liked_count", "collected_count", "comment_count", "share_count"):
            if k in interact:
                res[k] = interact[k]
    else:
        for k in ("liked_count", "collected_count", "comment_count", "share_count"):
            if k in note:
                res[k] = note[k]

    if "image_list" in note and isinstance(note["image_list"], list):
        res["images"] = [
            img["url"] for img in note["image_list"] if isinstance(img, dict) and "url" in img
        ]

    if "tag_list" in note and isinstance(note["tag_list"], list):
        res["tags"] = [
            tag["name"] for tag in note["tag_list"] if isinstance(tag, dict) and "name" in tag
        ]

    if "comments" in note and isinstance(note["comments"], list):
        res["comments"] = []
        for c in note["comments"]:
            if isinstance(c, dict):
                user_info = c.get("user_info") or {}
                uname = user_info.get("nickname", "") if isinstance(user_info, dict) else str(c.get("user", ""))
                res["comments"].append({
                    "content": c.get("content", ""),
                    "user": uname,
                    "like_count": c.get("like_count", 0),
                    "sub_comment_count": c.get("sub_comment_count", 0),
                })

    return res


def format_xhs_result(data):
    """Clean and structure raw xiaohongshu-mcp output."""
    if not isinstance(data, (dict, list)):
        return data
    if not data:
        return data
    if isinstance(data, list):
        return [format_xhs_result(x) for x in data]
    if "items" in data and isinstance(data["items"], list):
        return [format_xhs_result(x) for x in data["items"]]
    if "note_card" in data:
        return _format_single_note(data["note_card"])
    return _format_single_note(data)


class XiaoHongShuChannel(Channel):
    name = "xiaohongshu"
    description = "XiaoHongShu Posts and Notes"
    backends = ["OpenCLI", "xiaohongshu-mcp", "xhs-cli (xiaohongshu-cli)"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        from deep_scrape.utils.url import host_matches

        return host_matches(url, "xiaohongshu.com", "xhslink.com")

    def check(self, config=None):
        self.active_backend = None
        findings = []

        for backend in self.ordered_backends(config):
            if backend == "OpenCLI":
                result = self._check_opencli()
            elif backend == "xiaohongshu-mcp":
                result = self._check_mcp()
            else:
                result = self._check_xhs_cli()
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
            "No XiaoHongShu backend installed. Recommendations:\n"
            "  Desktop: deepscrape install --system --channels opencli\n"
            "           (reuses Chrome login session, zero config)\n"
            f"  Server: xiaohongshu-mcp: {_MCP_INSTALL_URL}\n"
            "           configure cookies via Cookie-Editor: deepscrape configure xhs-cookies"
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
                "OpenCLI bridge connected, but XiaoHongShu session and live commands are not verified; "
                "Doctor does not execute platform commands to avoid side effects."
            )
        return "warn", st.hint

    def _check_mcp(self):
        """xiaohongshu-mcp candidate. None = service not running."""
        if not _mcp_service_reachable():
            return None
        if not shutil.which("mcporter"):
            return "warn", (
                "xiaohongshu-mcp service reachable, but mcporter is not installed. Install:\n"
                "  npm install -g mcporter"
            )
        try:
            inspection = inspect_mcporter_config()
        except McporterConfigError as exc:
            return "error", f"mcporter configuration check failed: {exc}"
        if "xiaohongshu" in inspection.server_names:
            return "warn", (
                "xiaohongshu-mcp service reachable and registered with mcporter; Doctor does not "
                "verify live login credentials. Export cookies with Cookie-Editor if needed:\n"
                "  deepscrape configure xhs-cookies"
            )
        if inspection.imports_unchecked:
            return "warn", (
                "xiaohongshu-mcp service reachable; mcporter local config did not define xiaohongshu "
                "and editor imports are unchecked."
            )
        return "warn", (
            "xiaohongshu-mcp service running but not connected to mcporter. Run:\n"
            f"  mcporter config add xiaohongshu {_MCP_ENDPOINT} --scope home"
        )

    def _check_xhs_cli(self):
        """Inspect saved xhs-cli cookies without invoking browser extraction."""
        if not shutil.which("xhs"):
            return None
        cookie_path = home_dir() / ".xiaohongshu-cli" / "cookies.json"
        try:
            payload = read_small_text_no_follow(
                cookie_path,
                max_bytes=_MAX_XHS_COOKIE_BYTES,
            )
        except PrivatePathError as exc:
            return "warn", (
                f"xhs-cli installed, but cookies.json cannot be safely read: {exc}."
            )
        except OSError:
            return "warn", (
                "xhs-cli installed, but cookies.json cannot be safely read; "
                "Doctor does not run `xhs status`."
            )
        if payload is None:
            return self._xhs_cookie_hint()
        try:
            data = json.loads(payload)
        except (UnicodeError, json.JSONDecodeError, ValueError):
            return "warn", (
                "xhs-cli installed, but cookies.json cannot be safely parsed; "
                "Doctor does not run `xhs status`."
            )
        if not isinstance(data, dict) or not data.get("a1"):
            return self._xhs_cookie_hint()
        saved_at = data.get("saved_at")
        if isinstance(saved_at, (int, float)) and (
            time.time() - saved_at > _XHS_COOKIE_TTL_SECONDS
        ):
            return "warn", (
                "xhs-cli installed; saved cookies are older than 7 days. Doctor does not auto-refresh; "
                "please update explicitly using Cookie-Editor."
            )
        return "warn", (
            "xhs-cli installed with explicit saved cookies; Doctor does not run `xhs status` "
            "to prevent automatic browser cookie modifications."
        )

    @staticmethod
    def _xhs_cookie_hint():
        return "warn", (
            "xhs-cli installed but no valid explicit cookies found. Do not run `xhs login/status` "
            "which reads browser files automatically; migrate to xiaohongshu-mcp and export cookies "
            "with Cookie-Editor, then run `deepscrape configure xhs-cookies`."
        )
