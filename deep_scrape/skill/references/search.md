# Search Engine Guide

Autonomous AI semantic web and technical discovery via Exa AI.

## Exa AI Search

Exa is an AI-native search engine optimized for structured, semantic, and developer queries.

```bash
# General web search
mcporter call exa.web_search_exa query="B2B lead generation architecture" numResults=5

# Technical documentation and code examples
mcporter call exa.web_search_exa query="Playwright stealth scraping python example" numResults=5
```

### Common Query Scenarios

| Scenario | Command Pattern |
|----------|-----------------|
| General Web Discovery | `mcporter call exa.web_search_exa query="query" numResults=5` |
| Targeted Domain Research | `mcporter call exa.web_search_exa query="site:reddit.com cold outreach tips" numResults=5` |
| Code & Framework Docs | `mcporter call exa.web_search_exa query="FastAPI background tasks tutorial" numResults=5` |

### Key Features
- Clean semantic relevance filtering
- Superior technical and developer documentation discovery
- Free and requires no API key when accessed via mcporter
