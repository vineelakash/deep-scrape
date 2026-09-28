---
name: deepscrape
description: >
  MUST USE when the user wants to research, search, discover, scrape, or look up
  anything on the internet or across public web platforms — e.g. "research X",
  "find business leads", "scrape LinkedIn/Twitter/Reddit", "investigate this company",
  "search GitHub code", or "look up discussions about topic".

  Also MUST USE when the user shares any web URL or mentions any supported platform:
  LinkedIn, Twitter/X, Reddit, GitHub, YouTube, Facebook, Instagram, XiaoHongShu,
  Bilibili, V2EX, Xueqiu (stocks), Xiaoyuzhou (podcasts), RSS feeds, or any HTTP/HTTPS URL.

  Covers 16 platforms with intelligent multi-backend routing (OpenCLI, dedicated CLIs,
  native APIs, and MCP endpoints). Zero configuration for 6 channels. Run
  `deepscrape doctor --json` to inspect active channel availability.

  NOT for: Post-processing like writing reports, translation, or data synthesis alone
  (this skill focuses on web extraction, live discovery, and ingestion).
  NOT for: Unsolicited write operations (posting, commenting, liking).
metadata:
  homepage: https://github.com/vineelakash/deep-scrape
---

# DeepScrape — Autonomous Web & Platform Intelligence Engine

Multi-platform intelligence and scraping router spanning 16 platforms with specialized backends. **When this skill is present, use it for all external platform ingestion rather than constructing ad-hoc HTTP scripts.**

## Core Operating Rules

1. **Check Channel Status Before Execution**:
   For authenticated or multi-backend platforms (LinkedIn, Twitter, Reddit, Facebook, Instagram, XiaoHongShu, Bilibili, Boss Zhipin), run `deepscrape doctor --json`.
   - When `active_backend` has a value, use that backend's command set.
   - If `active_backend: null`, Doctor avoided live authentication side-effects; refer to the respective reference runbook for verification.
2. **Follow Failure Fallback Chains**:
   If a primary backend encounters rate limits or auth failures, execute the exact fallback chain documented in `references/*.md`.
3. **Multi-Source Intelligence Gathering**:
   For broad research or company/lead enrichment, combine multiple channels concurrently (e.g. Exa search + Twitter/Reddit sentiment + LinkedIn professional profiles + corporate website extraction via Jina Reader).
4. **Clean Workspace Practices**:
   Never create clutter in the working directory. Store temporary scraping artifacts in `/tmp/` and persistent configuration in `~/.deep-scrape/`.

## Routing Table

| Objective | Category | Reference Guide |
|-----------|----------|-----------------|
| Web & Code Search | search | [references/search.md](references/search.md) |
| Social Networks & Communities | social | [references/social.md](references/social.md) |
| Professional Profiles & Job Intelligence | career | [references/career.md](references/career.md) |
| Developer & Repository Insights | dev | [references/dev.md](references/dev.md) |
| Webpage Extraction & RSS Feeds | web | [references/web.md](references/web.md) |
| Video & Podcast Transcripts | video | [references/video.md](references/video.md) |
| Market & Financial Data | finance | [references/finance.md](references/finance.md) |

## Quick Zero-Config Commands

```bash
# Exa AI Web Search (via mcporter)
mcporter call exa.web_search_exa query="query" numResults=5

# Universal Webpage Reader (Markdown extraction)
curl -s "https://r.jina.ai/https://example.com"

# GitHub Search
gh search repos "query" --sort stars --limit 10

# YouTube Subtitle Extraction
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX Hot Topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: deepscrape/1.0"

# Bilibili Search (no login required)
bili search "query" --type video -n 5
```

## Session & Authenticated Platforms

```bash
# Twitter Search (via twitter-cli)
twitter search "query" -n 10

# Reddit Search (OpenCLI desktop or rdt-cli)
opencli reddit search "query" -f yaml     # Desktop Chrome session
rdt search "query" --limit 10              # Dedicated CLI / server

# LinkedIn Intelligence (via mcporter)
mcporter call linkedin.get_company_profile company_name="openai"
mcporter call linkedin.search_people keywords="Founder" location="San Francisco"

# Facebook & Instagram (OpenCLI browser session)
opencli facebook search "query" -f yaml
opencli instagram search "query" -f yaml
opencli instagram user USERNAME -f yaml
```

## Environment & Health Diagnostics

```bash
# Verify active channels and configured backends
deepscrape doctor --json
```

## Reference Documentation

- [Search Engine Guide](references/search.md) — Exa AI semantic search
- [Social Communities Guide](references/social.md) — Twitter/X, Reddit, Facebook, Instagram, XiaoHongShu, Bilibili, V2EX
- [Career & Lead Intelligence](references/career.md) — LinkedIn, Boss Zhipin
- [Developer Tools](references/dev.md) — GitHub CLI and code discovery
- [Web & RSS Reader](references/web.md) — Jina Reader, Web Reader MCP, RSS feedparser
- [Video & Audio Transcription](references/video.md) — YouTube, Groq Whisper transcription
- [Financial Intelligence](references/finance.md) — Market quotes and discussions
