# Groq Whisper Setup Guide

## Overview
When YouTube or podcast audio lacks subtitles, Groq's Whisper API delivers ultra-fast, high-accuracy speech-to-text transcription. Groq offers a generous free tier.

## Automated Setup Steps

1. Check configuration status:
```bash
deepscrape doctor | grep -i "groq\|whisper"
```

2. Store the user-provided key:
```python
from deep_scrape.config import Config
c = Config()
c.set("groq_api_key", "USER_API_KEY")
```

3. Test API connectivity:
```bash
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer USER_API_KEY" \
  -o /dev/null -w "%{http_code}"
```
Returns `200` on success.

## Instructions for User

> Audio and video speech-to-text requires a free Groq API key:
>
> 1. Visit https://console.groq.com
> 2. Sign up or log in
> 3. Navigate to "API Keys" in the left sidebar
> 4. Click "Create API Key"
> 5. Copy and provide the generated key

## Agent Actions upon Receiving Key

1. Save configuration: `config.set("groq_api_key", key)`
2. Verify API accessibility
3. Notify user: "✅ Audio transcription enabled! Videos and audio without subtitles can now be transcribed."
