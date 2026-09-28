# Cookie Export Guide — For Server & Headless Environments

When running on a remote server or headless environment, use these instructions to securely transfer authenticated sessions from your local browser.

## Recommended: Cookie-Editor Extension

1. Install **Cookie-Editor** for Chrome, Edge, or Firefox:
   https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm
2. Navigate to the desired website (e.g. `https://x.com` or `https://reddit.com`) and ensure you are logged in.
3. Click the Cookie-Editor icon in your toolbar.
4. Click **Export** → **Header String**.
5. Pass the exported string securely into DeepScrape:

```bash
# Twitter / X
deepscrape configure twitter-cookies

# XiaoHongShu
deepscrape configure xhs-cookies
```

Both commands prompt for hidden input so secrets are not exposed in terminal history or process tables. For CI/CD automation, pass values via `--stdin`:

```bash
cat cookies.txt | deepscrape configure twitter-cookies --stdin
```

## Supported Export Targets

| Platform | URL | Configuration Command |
|---|---|---|
| Twitter / X | https://x.com | `deepscrape configure twitter-cookies` |
| XiaoHongShu | https://www.xiaohongshu.com | `deepscrape configure xhs-cookies` |
| Xueqiu | https://xueqiu.com | `deepscrape configure --from-browser chrome --platform xueqiu` |
