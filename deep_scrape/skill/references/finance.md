# Financial & Market Intelligence

Stock quotes, company financial updates, and investor discussions.

## Diagnostic Verification

```bash
deepscrape doctor --json
```

## OpenCLI (Desktop Chrome Session)

```bash
# Verify session authentication
opencli xueqiu whoami -f yaml

# Stock search and live quotes
opencli xueqiu search "Nvidia" -f yaml
opencli xueqiu stock NVDA -f yaml

# Trending community discussions and top stocks
opencli xueqiu hot -f yaml
opencli xueqiu hot-stock -f yaml

# View all available read-only commands
opencli xueqiu --help
```

## Authentication Guidance
OpenCLI reuses existing browser sessions. To configure minimal cookies for headless/server use:
```bash
deepscrape configure --from-browser chrome --platform xueqiu
```
