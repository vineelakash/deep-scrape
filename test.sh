#!/usr/bin/env bash
set -euo pipefail

echo "Running DeepScrape Test Suite..."
pytest -v
ruff check deep_scrape tests
