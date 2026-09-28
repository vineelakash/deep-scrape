# Twitter/X Setup Guide (twitter-cli)

Basic tweet reading is supported via Jina Reader without authentication.

Advanced functionality uses twitter-cli (@public-clis/twitter-cli):
- Search tweets (`twitter search`)
- Read complete tweets and conversational threads (`twitter tweet`, `twitter thread`)
- User timelines (`twitter timeline`)
- Long-form articles (`twitter article`)

twitter-cli is an open-source tool, but requires authenticated Twitter cookies.

## Quick Setup

1. Check installation:
```bash
which twitter && echo "installed" || echo "not installed"
```

2. Install twitter-cli:
```bash
pipx install twitter-cli
```

3. Confirm command availability:
```bash
twitter --help
```

## Cookie Setup (Recommended: Cookie-Editor)

1. Install the [Cookie-Editor](https://cookie-editor.com/) browser extension
2. Log into x.com in your browser
3. Click Cookie-Editor icon → Export → Header String
4. Run configuration:
```bash
deepscrape configure twitter-cookies
```

This extracts `auth_token` and `ct0`, securely saving them to `~/.deep-scrape/config.yaml`.

For standalone CLI use, export them directly in your shell:
```bash
export TWITTER_AUTH_TOKEN="your_auth_token"
export TWITTER_CT0="your_ct0"
twitter search "test" -n 1
```

## Proxy Configuration

twitter-cli respects standard proxy environment variables:
```bash
export HTTP_PROXY="http://user:pass@host:port"
export HTTPS_PROXY="http://user:pass@host:port"
twitter search "ai intelligence" -n 5
```
