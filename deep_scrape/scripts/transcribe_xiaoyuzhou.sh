#!/bin/bash
# Xiaoyuzhou podcast transcription script
# Usage: bash transcribe.sh [--polish] <xiaoyuzhou-url> [output-file]
# Environment: GROQ_API_KEY (required)
#
# --polish: Calls Groq Llama 3.3 70B after transcription to format punctuation and paragraph breaks

set -e

POLISH=0
while [ $# -gt 0 ]; do
    case "$1" in
        --polish) POLISH=1; shift ;;
        --) shift; break ;;
        -h|--help)
            echo "Usage: bash transcribe.sh [--polish] <xiaoyuzhou-url> [output-file]"
            exit 0 ;;
        --*)
            echo "Unknown option: $1" >&2
            exit 1 ;;
        *) break ;;
    esac
done

URL="${1:?Usage: bash transcribe.sh [--polish] <xiaoyuzhou-url> [output-file]}"
OUTPUT="${2:-}"

PYTHON_CMD=()
ensure_python() {
    if [ "${#PYTHON_CMD[@]}" -gt 0 ]; then
        return 0
    fi
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD=(python3)
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD=(python)
    elif command -v py >/dev/null 2>&1; then
        PYTHON_CMD=(py -3)
    else
        echo "❌ Python not found (tried python3, python, py -3)" >&2
        return 1
    fi
}

ensure_python || exit 1
if ! XIAOYUZHOU_URL="$URL" "${PYTHON_CMD[@]}" <<'PY'
import os
from urllib.parse import urlsplit

try:
    parsed = urlsplit(os.environ["XIAOYUZHOU_URL"])
    hostname = (parsed.hostname or "").lower()
except ValueError:
    raise SystemExit(1)

allowed_host = (
    hostname == "xiaoyuzhoufm.com"
    or hostname.endswith(".xiaoyuzhoufm.com")
)
raise SystemExit(0 if parsed.scheme.lower() in {"http", "https"} and allowed_host else 1)
PY
then
    echo "❌ Only http/https URLs from xiaoyuzhoufm.com and its subdomains are supported" >&2
    exit 1
fi

# Try environment variable first, then ~/.deep-scrape/config.yaml
if [ -z "$GROQ_API_KEY" ]; then
    CONFIG_FILE="$HOME/.deep-scrape/config.yaml"
    if [ -f "$CONFIG_FILE" ]; then
        ensure_python || exit 1
        CONFIG_FOR_PYTHON="$CONFIG_FILE"
        if command -v cygpath >/dev/null 2>&1; then
            CONFIG_FOR_PYTHON=$(cygpath -w "$CONFIG_FILE")
        fi
        GROQ_API_KEY=$(DEEP_SCRAPE_CONFIG_FILE="$CONFIG_FOR_PYTHON" \
            "${PYTHON_CMD[@]}" -c 'import os, yaml; r = open(os.environ["DEEP_SCRAPE_CONFIG_FILE"], "r", encoding="utf-8"); content = r.read(32 * 1024 * 1024 + 1); r.close(); print((yaml.safe_load(content) or {}).get("groq_api_key", ""))' \
            2>/dev/null || true)
    fi
fi
GROQ_API_KEY="${GROQ_API_KEY:?Please set GROQ_API_KEY environment variable or run deepscrape configure groq-key}"

# Groq API limits: 25MB per file
MAX_CHUNK_SIZE_MB=20
AUDIO_BITRATE="64k"
CURL_CONNECT_TIMEOUT=15
PAGE_TIMEOUT=60
AUDIO_TIMEOUT=1800
GROQ_TIMEOUT=600
MAX_PAGE_BYTES=5242880
MAX_AUDIO_BYTES=1073741824
MAX_API_RESPONSE_BYTES=33554432
MAX_DURATION_SECONDS=10800

TEMP_ROOT="${TMPDIR:-/tmp}"
if ! WORK_DIR=$(mktemp -d "${TEMP_ROOT%/}/deepscrape-xiaoyuzhou.XXXXXX"); then
    echo "❌ Could not create temporary directory" >&2
    exit 1
fi

cleanup() {
    rm -rf -- "$WORK_DIR"
}
trap cleanup EXIT

echo "📻 Xiaoyuzhou Podcast Transcription"
echo "===================================="

# Step 1: Extract audio URL and title
echo "🔍 Resolving page..."
PAGE=$(curl --fail --show-error --location --silent \
    --connect-timeout "$CURL_CONNECT_TIMEOUT" \
    --max-time "$PAGE_TIMEOUT" \
    --max-filesize "$MAX_PAGE_BYTES" \
    "$URL")
AUDIO_URL=$(echo "$PAGE" | perl -ne 'while (/(https:\/\/media\.xyzcdn\.net\/[^"]*\.(?:m4a|mp3))/gi) { print "$1\n" }' | head -1)
TITLE=$(echo "$PAGE" | perl -ne 'if (/"title":"([^"]*)"/) { print "$1\n"; last }' | head -1)

if [ -z "$AUDIO_URL" ]; then
    echo "❌ Could not extract audio URL from page"
    exit 1
fi

echo "📝 Title: $TITLE"
echo "🔗 Audio: $AUDIO_URL"

# Step 2: Download audio
echo "⬇️  Downloading audio..."
EXT="${AUDIO_URL##*.}"
curl --fail --show-error --location --silent \
    --connect-timeout "$CURL_CONNECT_TIMEOUT" \
    --max-time "$AUDIO_TIMEOUT" \
    --max-filesize "$MAX_AUDIO_BYTES" \
    -o "$WORK_DIR/original.$EXT" \
    "$AUDIO_URL"
FILE_SIZE=$(ls -lh "$WORK_DIR/original.$EXT" | awk '{print $5}')
echo "📦 File size: $FILE_SIZE"

# Step 3: Get duration
if ! DURATION_RAW=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 \
    "$WORK_DIR/original.$EXT" 2>/dev/null); then
    echo "❌ ffprobe failed to read audio duration" >&2
    exit 1
fi
if DURATION=$(DURATION_RAW="$DURATION_RAW" MAX_DURATION_SECONDS="$MAX_DURATION_SECONDS" \
    "${PYTHON_CMD[@]}" -c '
import os
import sys
from decimal import Decimal, InvalidOperation

raw = os.environ["DURATION_RAW"]
try:
    value = Decimal(raw)
except InvalidOperation:
    raise SystemExit(2)
if not value.is_finite() or value < 0:
    raise SystemExit(2)
if value > Decimal(os.environ["MAX_DURATION_SECONDS"]):
    raise SystemExit(3)
print(int(value))
'); then
    :
else
    duration_status=$?
    if [ "$duration_status" -eq 3 ]; then
        echo "❌ Audio duration exceeds 3-hour limit" >&2
    else
        echo "❌ ffprobe returned invalid duration: ${DURATION_RAW:-<empty>}" >&2
    fi
    exit 1
fi
DURATION_MIN=$((DURATION / 60))
DURATION_SEC=$((DURATION % 60))
echo "⏱️  Duration: ${DURATION_MIN}m ${DURATION_SEC}s"

# Step 4: Transcode to mono MP3
echo "🔄 Transcoding..."
ffmpeg -y -i "$WORK_DIR/original.$EXT" -t "$MAX_DURATION_SECONDS" -b:a "$AUDIO_BITRATE" -ac 1 "$WORK_DIR/mono.mp3" 2>/dev/null
MONO_SIZE=$(stat -c%s "$WORK_DIR/mono.mp3" 2>/dev/null || stat -f%z "$WORK_DIR/mono.mp3")
MONO_SIZE_MB=$(awk -v bytes="$MONO_SIZE" 'BEGIN { printf "%.1f", bytes / 1024 / 1024 }')
echo "📦 Transcoded size: ${MONO_SIZE_MB}MB"

# Step 5: Chunking if required
MAX_BYTES=$((MAX_CHUNK_SIZE_MB * 1024 * 1024))

if [ "$MONO_SIZE" -le "$MAX_BYTES" ]; then
    cp "$WORK_DIR/mono.mp3" "$WORK_DIR/chunk_0.mp3"
    NUM_CHUNKS=1
    echo "📎 Single chunk sufficient"
else
    NUM_CHUNKS=$(( (MONO_SIZE / MAX_BYTES) + 1 ))
    CHUNK_DURATION=$(( DURATION / NUM_CHUNKS + 10 ))
    echo "✂️  Splitting into $NUM_CHUNKS chunks (~$((CHUNK_DURATION / 60))m each)..."
    
    for i in $(seq 0 $((NUM_CHUNKS - 1))); do
        START=$((i * CHUNK_DURATION))
        ffmpeg -y -i "$WORK_DIR/mono.mp3" -ss "$START" -t "$CHUNK_DURATION" -c copy "$WORK_DIR/chunk_${i}.mp3" 2>/dev/null
        CHUNK_SIZE=$(ls -lh "$WORK_DIR/chunk_${i}.mp3" | awk '{print $5}')
        echo "   Chunk $((i+1))/$NUM_CHUNKS: $CHUNK_SIZE"
    done
fi

# Step 6: Groq Whisper API transcription
echo "🎙️  Transcribing (Groq Whisper large-v3)..."

for i in $(seq 0 $((NUM_CHUNKS - 1))); do
    echo -n "   Chunk $((i+1))/$NUM_CHUNKS... "
    
    RESPONSE=$(curl --silent --show-error \
        --connect-timeout "$CURL_CONNECT_TIMEOUT" \
        --max-time "$GROQ_TIMEOUT" \
        --max-filesize "$MAX_API_RESPONSE_BYTES" \
        -w "\n%{http_code}" \
        https://api.groq.com/openai/v1/audio/transcriptions \
        -H "Authorization: Bearer $GROQ_API_KEY" \
        -F file="@$WORK_DIR/chunk_${i}.mp3" \
        -F model="whisper-large-v3" \
        -F language="zh" \
        -F response_format="text")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" != "200" ]; then
        echo "❌ API Error (HTTP $HTTP_CODE)"
        echo "$BODY"
        
        if [ "$HTTP_CODE" = "429" ]; then
            WAIT_SEC=$(echo "$BODY" | perl -ne 'if (/in (\d+)m/) { print "$1\n"; exit }')
            WAIT_SEC=${WAIT_SEC:-2}
            WAIT_SEC=$((WAIT_SEC * 60 + 30))
            if [ "$WAIT_SEC" -gt 900 ]; then
                WAIT_SEC=900
            fi
            echo "   ⏳ Rate limit encountered, waiting ${WAIT_SEC}s..."
            sleep "$WAIT_SEC"
            RESPONSE=$(curl --silent --show-error \
                --connect-timeout "$CURL_CONNECT_TIMEOUT" \
                --max-time "$GROQ_TIMEOUT" \
                --max-filesize "$MAX_API_RESPONSE_BYTES" \
                -w "\n%{http_code}" \
                https://api.groq.com/openai/v1/audio/transcriptions \
                -H "Authorization: Bearer $GROQ_API_KEY" \
                -F file="@$WORK_DIR/chunk_${i}.mp3" \
                -F model="whisper-large-v3" \
                -F language="zh" \
                -F response_format="text")
            HTTP_CODE=$(echo "$RESPONSE" | tail -1)
            BODY=$(echo "$RESPONSE" | sed '$d')
            
            if [ "$HTTP_CODE" != "200" ]; then
                echo "   ❌ Retry failed"
                exit 1
            fi
        else
            exit 1
        fi
    fi
    
    echo "$BODY" > "$WORK_DIR/transcript_${i}.txt"
    CHARS=$(wc -m < "$WORK_DIR/transcript_${i}.txt")
    echo "✅ ($CHARS characters)"
done

# Step 7: Combine output
echo "📄 Merging transcript..."

if [ -z "$OUTPUT" ]; then
    if ! OUTPUT=$(mktemp "${TEMP_ROOT%/}/deepscrape-transcript.XXXXXX"); then
        echo "❌ Could not create output file" >&2
        exit 1
    fi
fi

{
    echo "# $TITLE"
    echo ""
    echo "Source: $URL"
    echo "Duration: ${DURATION_MIN}m ${DURATION_SEC}s"
    echo "Transcribed: $(date '+%Y-%m-%d %H:%M')"
    echo ""
    echo "---"
    echo ""

    for i in $(seq 0 $((NUM_CHUNKS - 1))); do
        cat "$WORK_DIR/transcript_${i}.txt"
        echo ""
    done
} > "$OUTPUT"

TOTAL_CHARS=$(wc -m < "$OUTPUT")
echo ""
echo "✅ Finished!"
echo "📄 Output: $OUTPUT"
echo "📊 Total characters: $TOTAL_CHARS"
echo "===================================="
