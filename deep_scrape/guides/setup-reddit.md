# Reddit Setup Guide

## Overview

Reddit enforces strict anti-bot protections on non-browser requests (returning 403 on standard JSON endpoints).

DeepScrape supports Reddit search and extraction through **OpenCLI** (desktop) or **rdt-cli** (server/CLI):
- **Search**: `rdt search "keyword"`
- **Read Full Posts & Comments**: `rdt read POST_ID`

Free to use; requires a logged-in user session (`rdt login` or OpenCLI browser bridge).

## Automated Setup Steps

1. Check if rdt-cli is installed:
```bash
which rdt && echo "installed" || echo "not installed"
```

2. Install rdt-cli if needed:
```bash
pipx install 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66'
```

Or install via DeepScrape:
```bash
deepscrape install --env=auto --system --channels=reddit
```

## Usage Examples

Search Reddit:
```bash
rdt search "python best practices" -n 5
```

Read full post and comments:
```bash
rdt read POST_ID
```

## Fallback: Exa Search

If Exa is configured via mcporter, search Reddit directly:
```bash
mcporter call exa.web_search_exa query="site:reddit.com python best practices" numResults=5
```
