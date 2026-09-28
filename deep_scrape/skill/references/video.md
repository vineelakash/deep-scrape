# Video & Audio Intelligence

Extract metadata, download subtitles, and transcribe speech from YouTube, podcasts, and video platforms.

## YouTube (yt-dlp)

### Extract Metadata
```bash
yt-dlp --dump-json "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Extract Subtitles
```bash
# Download subtitles without video
yt-dlp --write-sub --write-auto-sub --sub-lang "en,es,zh-Hans" --skip-download -o "/tmp/%(id)s" "URL"

# Read extracted transcript
cat /tmp/VIDEO_ID.*.vtt
```

### Video Search
```bash
yt-dlp --dump-json "ytsearch5:autonomous ai agents"
```

## Speech-to-Text Audio Transcription (Groq Whisper)

When video or audio lacks subtitles, transcribe directly with Groq Whisper large-v3:

```bash
# Transcribe from YouTube URL
deepscrape transcribe "https://www.youtube.com/watch?v=VIDEO_ID"

# Transcribe local audio file
deepscrape transcribe ./audio.mp3 -o /tmp/transcript.txt
```

## Bilibili

```bash
# Video metadata and stats (no login required)
bili video BVxxx

# Search videos
bili search "topic" --type video -n 5

# Subtitles via OpenCLI (Desktop Chrome)
opencli bilibili subtitle BVxxx
```
