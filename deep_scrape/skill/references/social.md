# Social Media & Community Intelligence

Extract discussions, search posts, and monitor sentiment across Twitter/X, Reddit, Facebook, Instagram, XiaoHongShu, and V2EX.

## Twitter / X (twitter-cli)

### Authentication
Ensure `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` are configured:
```bash
deepscrape configure twitter-cookies
```

### Commands
```bash
# Search tweets
twitter search "AI agents architecture" -n 10

# Read individual tweet thread
twitter tweet TWEET_ID_OR_URL

# Home timeline
twitter feed -n 20

# User timeline
twitter timeline USERNAME -n 10
```

## Reddit

Reddit requires authenticated requests; direct JSON endpoints are blocked.

```bash
# Desktop (via OpenCLI Chrome session)
opencli reddit search "cold email SaaS" -f yaml
opencli reddit post POST_URL_OR_ID -f yaml

# CLI / Server (via rdt-cli)
rdt search "b2b outreach" --limit 10
rdt read POST_ID
```

## Facebook & Instagram (OpenCLI)

```bash
# Facebook
opencli facebook search "startups" -f yaml
opencli facebook feed -f yaml
opencli facebook groups -f yaml

# Instagram
opencli instagram search "tech founder" -f yaml
opencli instagram user USERNAME -f yaml
opencli instagram explore -f yaml
```

## XiaoHongShu (RED)

```bash
# Desktop (via OpenCLI)
opencli xiaohongshu search "SaaS tools" -f yaml
opencli xiaohongshu note "NOTE_URL_WITH_XSEC_TOKEN" -f yaml
opencli xiaohongshu comments NOTE_ID -f yaml

# Server (via xiaohongshu-mcp)
mcporter call xiaohongshu.search_feeds keyword="AI tools" --timeout 120000
```

## V2EX

```bash
# Hot topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: deepscrape/1.0"

# Node topics
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python" -H "User-Agent: deepscrape/1.0"
```
