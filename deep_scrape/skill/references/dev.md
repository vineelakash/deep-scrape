# Developer & Repository Tools

GitHub CLI integration for repository intelligence, issue inspection, PR analysis, and code search.

## GitHub (gh CLI)

```bash
# Authentication check
gh auth status

# Search repositories and code
gh search repos "lead intelligence" --sort stars --limit 10
gh search code "def extract_lead" --language python

# Inspect repository details
gh repo view owner/repo
gh repo clone owner/repo

# Issues & Pull Requests
gh issue list -R owner/repo --state open
gh issue view 123 -R owner/repo
gh pr list -R owner/repo --state open
gh pr view 123 -R owner/repo

# GitHub Actions CI runs
gh run list --repo owner/repo --limit 10
gh run view <run-id> --repo owner/repo --log-failed

# Direct GitHub API access with rate limit optimization
gh api /user
gh api repos/owner/repo
```
