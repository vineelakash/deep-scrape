# Exa Search Setup Guide

## Overview
Exa is an AI-native semantic search engine. Integrated via MCP, it is **free and requires no API key**. Once configured, it unlocks:
- Global semantic web search
- Targeted Reddit discovery (via `site:reddit.com`)
- Targeted Twitter/X discovery (via `site:x.com`)

## Automated Setup Steps

With explicit user authorization, running `deepscrape install --env=auto --system` performs the following steps automatically:

### 1. Install mcporter
```bash
npm install -g mcporter
```

### 2. Register Exa MCP
```bash
mcporter config add exa https://mcp.exa.ai/mcp --scope home
```

### 3. Verify Connectivity
```bash
deepscrape doctor
mcporter call exa.web_search_exa query="test" numResults=1
```

## Manual User Steps

**None.** Exa connects via MCP, free of charge, with zero registration and no API key required.

If `deepscrape install --system` encounters network issues during setup, run the two commands above manually.

## Frequently Asked Questions

**Q: Are there search rate limits?**
A: The public MCP endpoint is provided by Exa (mcp.exa.ai) and is currently free without restrictive limits.

**Q: What is mcporter?**
A: A lightweight CLI bridge for the Model Context Protocol (MCP) to invoke MCP servers directly from CLI or AI agents.
