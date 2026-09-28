# Webpage Extraction & RSS Feeds

Read any public web article, documentation page, or syndicated RSS/Atom feed.

## Universal Webpage Reader (Jina Reader)

```bash
# Read any webpage as clean Markdown
curl -s "https://r.jina.ai/https://example.com/blog/article"
```

**Use Case**: Zero-overhead extraction of blog posts, documentation, and news articles without maintaining headless browsers.

## Web Reader (MCP)

```bash
# Read webpage as structured Markdown
mcporter call web-reader.webReader url="https://example.com"

# Retain inline images
mcporter call web-reader.webReader url="https://example.com" retain_images=true

# Plain text format
mcporter call web-reader.webReader url="https://example.com" return_format="text"
```

## RSS / Atom Feeds (feedparser)

```python
python3 -c "
import feedparser
d = feedparser.parse('https://news.ycombinator.com/rss')
for e in d.entries[:5]:
    print(f'{e.title} -> {e.link}')
"
```
