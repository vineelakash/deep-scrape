# DeepScrape Troubleshooting Guide

## Xueqiu: API Returns HTTP 400

**Symptom:** `deepscrape doctor` displays warning for Xueqiu with `HTTP Error 400`.
**Cause:** Xueqiu requires minimal session cookies for reliable queries.
**Solution:** Log into xueqiu.com in Chrome, then run:
```bash
deepscrape configure --from-browser chrome --platform xueqiu
```
Rerun `deepscrape doctor` to verify recovery.

---

## Boss Zhipin: `boss status` reports logged in, but search returns `AUTH_EXPIRED`

**Symptom:** `boss status` reports `logged_in: true`, but queries return `AUTH_EXPIRED`.
**Cause:** Boss Zhipin maintains two distinct credential layers:
1. `~/.boss-agent/auth/session.enc`: Validates the local CLI state.
2. Dedicated Chrome browser profile: Contains the active session cookies used by CDP during live searches.

If the browser profile session expired, `boss status` may still report valid local tokens while CDP queries fail.
**Solution:**
1. Open dedicated Chrome:
   ```bash
   google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.boss-chrome-profile" "https://www.zhipin.com/web/geek/job"
   ```
2. Manually log in to zhipin.com in that window.
3. Synchronize session:
   ```bash
   boss --cdp-url http://localhost:9222 login --cdp
   deepscrape doctor
   ```

---

## Twitter / X: twitter-cli Connection Failures

**Symptom:** `twitter search` or `twitter feed` fails with authentication errors.
**Solution:**
Export cookies using Cookie-Editor (Header String), then run:
```bash
deepscrape configure twitter-cookies
```
Or set environment variables explicitly:
```bash
export TWITTER_AUTH_TOKEN="your_token"
export TWITTER_CT0="your_ct0"
```

---

## YouTube: Missing JS Runtime Warning

**Symptom:** `deepscrape doctor` reports `yt-dlp is installed but lacks a JS runtime`.
**Solution:**
Install Node.js or Deno:
```bash
# Node.js
npm install -g undici

# Or Deno
curl -fsSL https://deno.land/install.sh | sh
```
Then rerun:
```bash
deepscrape install --system
```
