# XiaoHongShu Setup Guide

## Overview
Read and search XiaoHongShu posts and notes. Desktop environments prefer OpenCLI; servers use [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp); xhs-cli is maintained as a legacy fallback.

## Prerequisites
- Desktop: Chrome browser with active logged-in XiaoHongShu session (via OpenCLI)
- Server: Docker container running xiaohongshu-mcp and Cookie-Editor export

## Authentication Policy
DeepScrape never reads browser cookies automatically or initiates headless logins.

Cookie setup for server environments:
1. Install [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
2. Log into xiaohongshu.com in browser
3. Export cookies via Cookie-Editor (Header String or JSON)
4. Run:
```bash
deepscrape configure xhs-cookies
deepscrape doctor
```

## Docker Server Setup
```bash
docker run -d \
  --name xiaohongshu-mcp \
  -p 18060:18060 \
  xpzouying/xiaohongshu-mcp

mcporter config add xiaohongshu http://localhost:18060/mcp --scope home
```
