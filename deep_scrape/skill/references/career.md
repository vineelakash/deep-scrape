# Career & Professional Lead Intelligence

LinkedIn professional profiles, company intelligence, and job discovery.

## LinkedIn

```bash
# Retrieve personal profile details
mcporter call linkedin.get_person_profile linkedin_username="username" sections="experience,education"

# Search professionals and decision makers
mcporter call linkedin.search_people keywords="AI engineer" location="Shanghai"

# Retrieve company intelligence
mcporter call linkedin.get_company_profile company_name="openai" sections="posts,jobs"

# Search job openings
mcporter call linkedin.search_jobs keywords="software engineer" location="Remote" max_pages=2
```

> **Setup**: Authenticate once by running `uvx mcp-server-linkedin@latest --login`.

### Fallback Option
If MCP is temporarily unavailable, use Jina Reader for public profiles:
```bash
curl -s "https://r.jina.ai/https://www.linkedin.com/in/username"
```

## Boss Zhipin

Recruitment search and JD analysis via CDP-connected dedicated Chrome instance (`boss-agent-cli`).

```bash
# Check connectivity status
deepscrape doctor

# Synchronize authenticated session
boss --cdp-url http://localhost:9222 login --cdp

# Execute strict CDP search without falling back to headless
boss --browser-source existing-browser --cdp-url http://localhost:9222 search "AI Architect"
```
