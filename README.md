# DeepScrape

> Autonomous high-precision web and platform scraping engine for AI agents and developer automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: MCP & CLI](https://img.shields.io/badge/Architecture-MCP%20%26%20CLI-success.svg)](#architecture)

DeepScrape equips AI agents with robust eyes to discover, ingest, search, and extract live data from 16 major web platforms. Instead of brittle custom scrapers or headless browsers that break under anti-bot heuristics, DeepScrape provides an intelligent multi-backend routing engine that leverages browser sessions, Model Context Protocol (MCP) servers, official CLIs, and direct API fallbacks.

---

## Key Features

- **16 Supported Platforms**: LinkedIn, Twitter/X, Reddit, GitHub, YouTube, Facebook, Instagram, XiaoHongShu, Bilibili, V2EX, Xueqiu (stocks), Xiaoyuzhou (podcasts), RSS/Atom feeds, and universal public webpages.
- **Smart Multi-Backend Routing**:
  - **OpenCLI**: Drives real desktop Chrome sessions with zero per-platform configuration for platforms like Reddit, Facebook, Instagram, and XiaoHongShu.
  - **Model Context Protocol (MCP)**: Native integration for Exa Semantic Search, LinkedIn, and remote browser services.
  - **Dedicated CLIs**: First-class support for `twitter-cli`, `rdt-cli`, `bili-cli`, `gh`, and `boss-agent-cli`.
  - **Fallback Endpoints**: Free high-speed Markdown extraction via Jina Reader and direct public APIs.
- **Zero-Config by Default**: 6 core channels work immediately out-of-the-box (Universal Web, YouTube, GitHub, Exa AI search, RSS feeds, and V2EX).
- **Comprehensive Diagnostic Engine (`deepscrape doctor`)**: Inspects every channel, verifies local dependencies, tests loopback sockets, and outputs actionable self-healing guidance.
- **Zero Browser Creep / Strict Security**:
  - Never reads or dumps browser credentials without explicit user consent.
  - Cookies and API tokens stored strictly in owner-restricted files (`~/.deep-scrape/`).
  - No continuous background daemon footprint.
- **Agent Skill Ready**: Ready for Claude Code, OpenCode, OpenClaw, Antigravity, and custom LLM agent frameworks.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/vineelakash/deep-scrape.git
cd deep-scrape

# Install with pip
pip install -e .
```

### Health Check

Run the built-in diagnostic doctor to verify active channels and available backends:

```bash
deepscrape doctor
```

Output format example:
```
DeepScrape Diagnostics Report
==================================================
[Tier 0 — Zero Configuration]
  ✅ Web Reader        | Jina Reader (active)
  ✅ Exa Search        | Exa via mcporter (active)
  ✅ GitHub            | gh CLI (active)
  ✅ YouTube           | yt-dlp (active)
  ✅ RSS Feeds         | feedparser (active)
  ✅ V2EX              | Public API (active)

[Tier 1 — Session / Credentials]
  ✅ Twitter/X         | twitter-cli
  ⚠️  Reddit            | OpenCLI (browser session)
  ⚠️  XiaoHongShu       | OpenCLI (browser session)
  ...
```

---

## Supported Channels & Capabilities

| Platform | Primary Backend | Capabilities | Zero Config? |
|---|---|---|---|
| **Web** | Jina Reader | Full-text Markdown extraction from any public URL | ✅ Yes |
| **Exa Search** | mcporter / Exa | AI semantic search, technical research, site filters | ✅ Yes |
| **GitHub** | `gh` CLI | Repo search, issues, pull requests, actions, code search | ✅ Yes |
| **YouTube** | `yt-dlp` | Metadata, subtitle extraction, auto-transcripts | ✅ Yes |
| **RSS / Atom** | `feedparser` | Syndicated feed parsing and monitoring | ✅ Yes |
| **V2EX** | Public API | Hot topics, node browsing, replies, user profiles | ✅ Yes |
| **LinkedIn** | `mcp-server-linkedin` | People search, company profiles, job postings | 🔑 Setup |
| **Twitter / X** | `twitter-cli` | Tweet search, full threads, user timelines | 🔑 Setup |
| **Reddit** | OpenCLI / `rdt-cli` | Subreddit search, post reading, threaded comments | 🔑 Setup |
| **Facebook** | OpenCLI | Posts, profile feeds, public groups | 🔑 Setup |
| **Instagram** | OpenCLI | User search, recent posts, exploration | 🔑 Setup |
| **XiaoHongShu** | OpenCLI / MCP | Note search, full post text, comments | 🔑 Setup |
| **Bilibili** | `bili-cli` / OpenCLI | Video search, hot lists, subtitles, audio extraction | ✅ Yes |
| **Xueqiu** | Xueqiu API | Real-time stock quotes, market trends, discussions | 🔑 Setup |
| **Xiaoyuzhou** | Groq Whisper | Podcast downloading and speech-to-text transcription | 🔑 Setup |
| **Boss Zhipin** | `boss-agent-cli` | CDP job search and JD extraction | 🔑 Setup |

---

## Usage Examples

### 1. Universal Web Extraction
Extract full clean Markdown from any article:
```bash
curl -s "https://r.jina.ai/https://example.com/blog/article"
```

### 2. Global AI Semantic Search (Exa)
```bash
mcporter call exa.web_search_exa query="enterprise lead intelligence architecture" numResults=5
```

### 3. Twitter / X Deep Ingestion
```bash
# Configure Twitter cookies (hidden prompt or --stdin)
deepscrape configure twitter-cookies

# Search tweets
twitter search "AI agents research" -n 10

# Read full conversational thread
twitter tweet TWEET_ID_OR_URL
```

### 4. Reddit Discovery
```bash
# Desktop (via OpenCLI Chrome session)
opencli reddit search "cold email SaaS" -f yaml

# Server (via rdt-cli)
rdt search "b2b outreach" --limit 10
rdt read POST_ID
```

### 5. Audio & Video Speech-to-Text Transcription
Transcribe YouTube videos or podcasts lacking native subtitles via Groq Whisper large-v3:
```bash
# Configure free Groq API key
deepscrape configure groq-key

# Transcribe directly from URL
deepscrape transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
```

---

## Agent Integration (Skill Setup)

To register DeepScrape with your AI coding agent (Claude Code, OpenCode, OpenClaw, Antigravity):

```bash
deepscrape skill --install
```

This installs `deepscrape/SKILL.md` and comprehensive reference documentation into your agent's skill directory (`~/.agents/skills/deepscrape`, `~/.claude/skills/deepscrape`, etc.).

---

## Project Structure

```
deep-scrape/
├── deep_scrape/            # Core Python package
│   ├── backends/           # Backend adapters (OpenCLI, etc.)
│   ├── channels/           # 16 platform channel drivers
│   ├── guides/             # Interactive setup & configuration runbooks
│   ├── integrations/       # MCP server integration
│   ├── scripts/            # Helper shell scripts (e.g. podcast transcription)
│   ├── skill/              # Agent skill definition & category reference docs
│   ├── utils/              # Security, path sanitation, and networking helpers
│   ├── cli.py              # CLI entry point (installer, doctor, configure)
│   ├── config.py           # Secure configuration management (~/.deep-scrape)
│   ├── core.py             # Main DeepScrape orchestration engine
│   ├── doctor.py           # Multi-tiered platform diagnostic checker
│   └── probe.py            # Non-destructive command and environment prober
├── docs/                   # User guides (installation, updates, cookie export)
├── tests/                  # Automated pytest suite
└── pyproject.toml          # Package configuration & entry points
```

---

## Security & Privacy Policy

- **No Secret Leaks**: Credentials are never echoed in CLI logs or command traces. Positional CLI secrets are deprecated in favor of secure hidden prompts and standard input pipes (`--stdin`).
- **Owner-Only Permissions**: All configuration files created in `~/.deep-scrape/` use restrictive permissions (`0600` / `0700`).
- **Explicit Browser Consent**: DeepScrape never executes stealth cookie theft. Browser cookies are imported only upon explicit user command.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
