# CLAUDE.md — DeepScrape Development Guide

## Build & Test Commands
- Run test suite: `pytest`
- Run single test: `pytest tests/test_doctor.py`
- Lint code: `ruff check deep_scrape tests`
- Format code: `ruff format deep_scrape tests`
- Type checking: `mypy deep_scrape`
- CLI test: `python -m deep_scrape.cli doctor`

## Architecture Rules
1. **Never write files in the active workspace**: Temporary files must be stored in `/tmp/`, configuration in `~/.deep-scrape/`.
2. **Read-Only Probing**: `doctor` checks and status probes must never produce side effects (e.g. executing commands that auto-read or modify browser cookies).
3. **Pure English**: Maintain 100% clean English for all docstrings, CLI outputs, and documentation.
