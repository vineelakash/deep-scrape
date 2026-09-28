# -*- coding: utf-8 -*-
"""Xueqiu — stock quotes, search, trending posts & hot stocks."""

import http.cookiejar
import json
import re
import urllib.parse
import urllib.request

from deep_scrape.utils.text import scrub_url_credentials

from .base import Channel

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
_TIMEOUT = 10
_MAX_RESPONSE_BYTES = 5 * 1024 * 1024

_cookie_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_cookie_jar))
_cookies_initialized = False


def _inject_cookie_string(raw: str):
    """Parse cookie header string and inject into _cookie_jar."""
    if not raw:
        return
    for part in raw.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookie = http.cookiejar.Cookie(
                version=0,
                name=k.strip(),
                value=v.strip(),
                port=None,
                port_specified=False,
                domain=".xueqiu.com",
                domain_specified=True,
                domain_initial_dot=True,
                path="/",
                path_specified=True,
                secure=False,
                expires=None,
                discard=True,
                comment=None,
                comment_url=None,
                rest={},
                rfc2109=False,
            )
            _cookie_jar.set_cookie(cookie)


def _load_cookies_from_config(config=None) -> bool:
    """Read saved Xueqiu cookies from config and load into _cookie_jar."""
    if config is None:
        return False
    try:
        raw = config.get("xueqiu_cookie") or config.get("xueqiu_cookies")
        if not raw:
            return False
        if isinstance(raw, dict):
            raw = "; ".join(f"{k}={v}" for k, v in raw.items())
        if isinstance(raw, str):
            _inject_cookie_string(raw)
            return True
    except Exception:
        pass
    return False


def _ensure_cookies(config=None):
    global _cookies_initialized
    if _cookies_initialized:
        return
    if not _load_cookies_from_config(config):
        try:
            req = urllib.request.Request("https://xueqiu.com", headers={"User-Agent": _UA})
            _opener.open(req, timeout=5)
        except Exception:
            pass
    _cookies_initialized = True


def _get_json(url: str, config=None, timeout: int = _TIMEOUT) -> dict:
    """Fetch Xueqiu URL and return parsed JSON."""
    _ensure_cookies(config)
    headers = {
        "User-Agent": _UA,
        "Accept": "application/json",
        "Referer": "https://xueqiu.com/",
    }
    req = urllib.request.Request(url, headers=headers)
    with _opener.open(req, timeout=timeout) as resp:
        body = resp.read()
    if len(body) > _MAX_RESPONSE_BYTES:
        raise ValueError(
            f"Xueqiu API response exceeds {_MAX_RESPONSE_BYTES} byte limit"
        )
    return json.loads(body.decode("utf-8"))


def _clean_text(text: str) -> str:
    """Clean HTML tags and entities."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
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


_strip_html = _clean_text


class XueqiuChannel(Channel):
    name = "xueqiu"
    description = "Xueqiu Stock Quotes and Community Updates"
    backends = ["Xueqiu API (Cookie recommended)"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        from deep_scrape.utils.url import host_matches

        return host_matches(url, "xueqiu.com")

    def check(self, config=None):
        self.active_backend = None
        try:
            data = _get_json(
                "https://stock.xueqiu.com/v5/stock/quote.json"
                "?symbol=SH601138&extend=detail",
                config,
            )
            quote = (data.get("data") or {}).get("quote") or {}
            if quote:
                self.active_backend = self.backends[0]
                return "ok", "Public API available (quotes, search, trending posts, hot stocks)"
            return "warn", "API response abnormal (empty data returned)"
        except Exception as e:
            detail = scrub_url_credentials(e).rstrip(": ")
            return "warn", (
                f"Xueqiu API connection failed: {detail}. "
                "To configure cookies: deepscrape configure --from-browser chrome --platform xueqiu; "
                "Doctor will not automatically read browser cookies."
            )

    def get_stock_quote(self, symbol: str) -> dict:
        """Get real-time stock quote."""
        encoded_symbol = urllib.parse.quote(symbol, safe="")
        data = _get_json(
            "https://stock.xueqiu.com/v5/stock/quote.json"
            f"?symbol={encoded_symbol}&extend=detail"
        )
        q = (data.get("data") or {}).get("quote") or {}
        return {
            "symbol": q.get("symbol", symbol),
            "name": q.get("name", ""),
            "current": q.get("current"),
            "percent": q.get("percent"),
            "volume": q.get("volume"),
            "pe_ttm": q.get("pe_ttm"),
            "pe_forecast": q.get("pe_forecast"),
            "pb": q.get("pb"),
            "eps": q.get("eps"),
            "chg": q.get("chg"),
            "high": q.get("high"),
            "low": q.get("low"),
            "open": q.get("open"),
            "last_close": q.get("last_close"),
            "amount": q.get("amount"),
            "market_capital": q.get("market_capital"),
            "turnover_rate": q.get("turnover_rate"),
            "timestamp": q.get("timestamp"),
        }

    def search_stock(self, query: str, limit: int = 10) -> list:
        """Search stocks by code or name."""
        encoded_q = urllib.parse.quote(query)
        data = _get_json(
            f"https://xueqiu.com/stock/search.json?code={encoded_q}&size={limit}"
        )
        stocks = data.get("stocks") or []
        results = []
        for s in stocks[:limit]:
            if not isinstance(s, dict):
                continue
            results.append({
                "symbol": s.get("code") or s.get("symbol", ""),
                "name": s.get("name", ""),
                "exchange": s.get("exchange", ""),
            })
        return results

    def get_hot_posts(self, limit: int = 20) -> list:
        """Get trending Xueqiu community posts."""
        if limit < 0:
            raise ValueError("Limit must be non-negative")
        if limit == 0:
            return []

        limit = min(limit, 50)
        data = _get_json(
            f"https://xueqiu.com/v4/statuses/public_timeline_by_category.json?category=-1&count={limit}"
        )
        items = data.get("list") or []
        results = []
        for item in items[:limit]:
            raw = item.get("data")
            if not isinstance(raw, str):
                results.append({
                    "id": 0,
                    "title": "",
                    "text": "",
                    "author": "",
                    "likes": 0,
                    "url": "",
                })
                continue
            try:
                inner = json.loads(raw)
            except Exception:
                results.append({
                    "id": 0,
                    "title": "",
                    "text": "",
                    "author": "",
                    "likes": 0,
                    "url": "",
                })
                continue
            user = inner.get("user") or {}
            target = inner.get("target") or ""
            target_url = f"https://xueqiu.com{target}" if target else ""
            results.append({
                "id": inner.get("id", 0),
                "title": _clean_text(inner.get("title", "")),
                "text": _clean_text(inner.get("text", ""))[:200],
                "author": user.get("screen_name", ""),
                "likes": inner.get("like_count", 0),
                "url": target_url,
            })
            if len(results) >= limit:
                break
        return results

    def get_hot_stocks(self, limit: int = 10, stock_type: int = 10) -> list:
        """Get trending stock rankings."""
        limit = min(limit, 50)
        data = _get_json(
            f"https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size={limit}&_type={stock_type}&type={stock_type}"
        )
        items = (data.get("data") or {}).get("items") or []
        results = []
        for rank, item in enumerate(items[:limit], 1):
            if not isinstance(item, dict):
                continue
            results.append({
                "rank": rank,
                "symbol": item.get("code") or item.get("symbol", ""),
                "name": item.get("name", ""),
                "current": item.get("current"),
                "percent": item.get("percent"),
            })
        return results
