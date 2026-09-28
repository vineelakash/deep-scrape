# DeepScrape — Installation Guide

## For Users

Copy this prompt to your AI Agent:

```
Install and configure DeepScrape: https://raw.githubusercontent.com/vineelakash/deep-scrape/main/docs/install.md
```

> 🛡️ **Safe by default:** Running `deepscrape install` performs read-only environment checks. To authorize system dependency installation, pass `--system`:
> ```bash
> deepscrape install --system --channels=all
> ```

---

## For AI Agents

### Objective
Install DeepScrape and configure the required upstream tools to enable full internet and multi-platform research. DeepScrape serves as the router, diagnostic checker, and configuration manager.

### ⚠️ Operational Boundaries
- **DO NOT** execute commands with `sudo` unless explicitly approved by the user.
- **DO NOT** modify files outside `~/.deep-scrape/`.
- **DO NOT** clone repositories or leave temporary files inside the active workspace directory.
- All temporary files must reside in `/tmp/` and persistent configuration in `~/.deep-scrape/`.

### Directory Layout
| Purpose | Directory Path |
|---|---|
| Configuration & Tokens | `~/.deep-scrape/config.yaml` |
| Tools & Binaries | `~/.deep-scrape/tools/` |
| Temporary Files | `/tmp/` |
| Agent Skills | `~/.agents/skills/deepscrape/` |

---

### Step 1: Install DeepScrape

```bash
pip install -e .
```

### Step 2: Install Core System Dependencies

```bash
# Node.js & npm (for OpenCLI & mcporter)
# macOS:
brew install node gh

# Debian / Ubuntu:
apt update && apt install -y nodejs npm gh

# Windows (PowerShell / WinGet):
winget install OpenJS.NodeJS
winget install GitHub.cli
```

### Step 3: Install MCP & Search Tools

```bash
# Install mcporter for MCP bridge
npm install -g mcporter

# Configure free Exa semantic search
mcporter config add exa https://mcp.exa.ai/mcp --scope home
```

### Step 4: Install Optional Platform Channels

```bash
# YouTube & Media Download
python -m pip install -U "yt-dlp[default]"

# Twitter / X CLI
pipx install twitter-cli

# Reddit CLI
pipx install 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66'

# Bilibili CLI
pipx install bilibili-cli

# Desktop Browser Session Bridge (OpenCLI)
npm install -g @jackwener/opencli

# LinkedIn MCP Server
uvx mcp-server-linkedin@latest --login
mcporter config add linkedin --command uvx --arg mcp-server-linkedin@latest --env UV_HTTP_TIMEOUT=300 --scope home

# Boss Zhipin CLI
boss --cdp-url http://localhost:9222 login --cdp
```

### Step 5: Verify Installation

```bash
deepscrape doctor
```
