# DeepScrape — Update Guide

## For Users

Copy this prompt to your AI Agent:

```
Update DeepScrape: https://raw.githubusercontent.com/vineelakash/deep-scrape/main/docs/update.md
```

---

## For AI Agents

### Step 1: Check Current Version
```bash
deepscrape check-update
```
If already up to date, run `deepscrape doctor` to verify health and exit.

### Step 2: Update Package
```bash
pip install --upgrade https://github.com/vineelakash/deep-scrape/archive/main.zip
```

### Step 3: Refresh Upstream Tools
Upgrade only previously installed tools:
```bash
which twitter >/dev/null 2>&1 && pipx upgrade twitter-cli
which bili    >/dev/null 2>&1 && pipx upgrade bilibili-cli
which yt-dlp  >/dev/null 2>&1 && pipx install --force 'yt-dlp[default]'
which opencli >/dev/null 2>&1 && npm update -g @jackwener/opencli
```

### Step 4: Refresh Agent Skill
```bash
deepscrape skill --install
```

### Step 5: Verify Health
```bash
deepscrape doctor
```
