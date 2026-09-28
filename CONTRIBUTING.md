# Contributing to DeepScrape

Thank you for your interest in contributing to DeepScrape! This document outlines development guidelines and standards.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/vineelakash/deep-scrape.git
cd deep-scrape

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

## Code Quality Standards

We enforce strict quality, security, and formatting checks:

- **ruff**: Linting and formatting
- **mypy**: Static type validation
- **pytest**: Automated test suite

```bash
# Check formatting & linting
ruff check deep_scrape tests
ruff format deep_scrape tests

# Run test suite
pytest
```

## Channel Contribution Contract

To add a new platform channel:
1. Create a module in `deep_scrape/channels/<channel_name>.py`.
2. Inherit from `deep_scrape.channels.base.Channel`.
3. Implement `can_handle(url)` and non-destructive `check(config)`.
4. Register the channel in `deep_scrape/channels/__init__.py`.
5. Add test coverage under `tests/`.
