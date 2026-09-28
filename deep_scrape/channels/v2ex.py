# -*- coding: utf-8 -*-
"""V2EX — public API for hot topics, node topics, topic details, and user profiles."""

import json
import shutil
import ssl
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from deep_scrape.utils.text import scrub_url_credentials

from .base import Channel

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
_TIMEOUT = 10
_MAX_RESPONSE_BYTES = 5 * 1024 * 1024


def _validate_api_url(url: str):
    parsed = urllib.parse.urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ("v2ex.com", "www.v2ex.com")
        or parsed.port not in (None, 443)
        or parsed.username
        or parsed.password
        or not parsed.path.startswith("/api/")
    ):
        raise ValueError(f"Only V2EX HTTPS API endpoints supported: {url}")


def _get_json_with_urllib(url: str, timeout: int = _TIMEOUT) -> dict | list:
    """Fetch URL using urllib and return parsed JSON."""
    _validate_api_url(url)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": _UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read(_MAX_RESPONSE_BYTES + 1)
    if len(body) > _MAX_RESPONSE_BYTES:
        raise ValueError(
            f"V2EX API response exceeds {_MAX_RESPONSE_BYTES} byte limit"
        )
    return json.loads(body.decode("utf-8"))


def _get_json(url: str, timeout: int = _TIMEOUT) -> dict | list:
    """Fetch URL with TLS EOF curl fallback."""
    _validate_api_url(url)
    try:
        return _get_json_with_urllib(url, timeout=timeout)
    except (urllib.error.URLError, ssl.SSLError) as exc:
        if "UNEXPECTED_EOF_WHILE_READING" in str(exc):
            curl_bin = shutil.which("curl")
            if curl_bin:
                cmd = [
                    curl_bin,
                    "--fail",
                    "--proto",
                    "=https",
                    "--max-time",
                    str(timeout),
                    "--max-filesize",
                    str(_MAX_RESPONSE_BYTES),
                    "--url",
                    url,
                ]
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout + 2,
                    check=True,
                )
                return json.loads(proc.stdout)
        raise


def _clean_text(text: str) -> str:
    """Unescape HTML entities and strip surrounding whitespace."""
    if not text:
        return ""
    for entity, char in [
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", '"'),
        ("&#39;", "'"),
        ("&nbsp;", " "),
    ]:
        text = text.replace(entity, char)
    return text.strip()


class V2EXChannel(Channel):
    name = "v2ex"
    description = "V2EX Community Discussions"
    backends = ["V2EX API (public)"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        from deep_scrape.utils.url import host_matches

        return host_matches(url, "v2ex.com")

    def check(self, config=None):
        try:
            _get_json(
                "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1"
            )
            self.active_backend = self.backends[0]
            return "ok", "Public API available (hot topics, node browsing, topic details, user profiles)"
        except Exception as e:
            self.active_backend = None
            return (
                "warn",
                f"V2EX API connection failed (may require proxy): {scrub_url_credentials(e)}",
            )

    def get_hot_topics(self, limit: int = 20) -> list:
        """Get list of hot topics."""
        data = _get_json("https://www.v2ex.com/api/topics/hot.json")
        if not isinstance(data, list):
            return []
        results = []
        for item in data[:limit]:
            if not isinstance(item, dict):
                continue
            node_info = item.get("node") or {}
            content = _clean_text(item.get("content", ""))
            results.append({
                "id": item.get("id"),
                "title": _clean_text(item.get("title", "")),
                "url": item.get("url", f"https://www.v2ex.com/t/{item.get('id', '')}"),
                "content": content[:200],
                "replies": item.get("replies", 0),
                "node_title": node_info.get("title", ""),
                "node_name": node_info.get("name", ""),
                "author": (item.get("member") or {}).get("username", ""),
                "created": item.get("created"),
            })
        return results

    def get_node_topics(self, node_name: str, page: int = 1, limit: int = 20) -> list:
        """Get recent topics for a specific node."""
        q = urllib.parse.urlencode({"node_name": node_name, "page": page})
        data = _get_json(f"https://www.v2ex.com/api/topics/show.json?{q}")
        if not isinstance(data, list):
            return []
        results = []
        for item in data[:limit]:
            if not isinstance(item, dict):
                continue
            node_info = item.get("node") or {}
            content = _clean_text(item.get("content", ""))
            results.append({
                "id": item.get("id"),
                "title": _clean_text(item.get("title", "")),
                "url": item.get("url", f"https://www.v2ex.com/t/{item.get('id', '')}"),
                "content": content[:200],
                "replies": item.get("replies", 0),
                "node_title": node_info.get("title", node_name),
                "node_name": node_name,
                "author": (item.get("member") or {}).get("username", ""),
                "created": item.get("created"),
            })
        return results

    def get_topic(self, topic_id: int | str) -> dict:
        """Get topic details and replies list."""
        topic_id_str = str(topic_id)
        q = urllib.parse.urlencode({"id": topic_id_str})
        data = _get_json(f"https://www.v2ex.com/api/topics/show.json?{q}")
        topic = (
            data[0]
            if isinstance(data, list) and data
            else (data if isinstance(data, dict) else {})
        )

        replies_q = urllib.parse.urlencode({"topic_id": topic_id_str, "page": 1})
        replies = []
        try:
            r_data = _get_json(
                f"https://www.v2ex.com/api/replies/show.json?{replies_q}"
            )
            if isinstance(r_data, list):
                for r in r_data:
                    if isinstance(r, dict):
                        replies.append({
                            "author": (r.get("member") or {}).get("username", ""),
                            "content": _clean_text(r.get("content", "")),
                            "created": r.get("created"),
                        })
        except Exception:
            replies = []

        encoded_path_id = urllib.parse.quote(topic_id_str, safe="")
        return {
            "id": topic.get("id", topic_id),
            "title": _clean_text(topic.get("title", "")),
            "url": topic.get("url") or f"https://www.v2ex.com/t/{encoded_path_id}",
            "content": _clean_text(topic.get("content", "")),
            "replies": replies,
            "author": (topic.get("member") or {}).get("username", ""),
            "node_name": (topic.get("node") or {}).get("name", ""),
            "created": topic.get("created"),
        }

    get_topic_detail = get_topic

    def get_user(self, username: str) -> dict:
        """Get user profile details."""
        q = urllib.parse.urlencode({"username": username})
        data = _get_json(f"https://www.v2ex.com/api/members/show.json?{q}")
        if not isinstance(data, dict):
            data = {}
        encoded_name = urllib.parse.quote(username, safe="")
        return {
            "id": data.get("id"),
            "username": data.get("username", username),
            "github": data.get("github", ""),
            "avatar": data.get("avatar_large") or data.get("avatar_normal") or "",
            "url": data.get("url") or f"https://www.v2ex.com/member/{encoded_name}",
            "location": data.get("location", ""),
            "website": data.get("website", ""),
            "twitter": data.get("twitter", ""),
            "bio": _clean_text(data.get("bio", "")),
        }

    get_user_profile = get_user

    def search(self, query: str) -> list:
        """Offline guidance search."""
        q = urllib.parse.urlencode({"q": query})
        return [
            {
                "error": (
                    "V2EX public API does not provide a search endpoint. "
                    f"Recommended alternative: https://www.google.com/search?{q}"
                )
            }
        ]

    search_topics = search
