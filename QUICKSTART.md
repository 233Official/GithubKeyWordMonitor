# Quick Start Guide

## Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install uv
   uv sync
   ```

2. **Configure:**
   ```bash
   cp config.toml.example config.toml
   # Edit config.toml and add your GitHub token
   ```

3. **Run:**
   ```bash
   uv run main.py
   ```

4. **Subscribe to RSS:**
   - Open `feed.xml` in your RSS reader

## GitHub Token

Get your token from: https://github.com/settings/tokens

Required scopes: `public_repo` (for public repositories)

## Example config.toml

```toml
github_token = "ghp_YourTokenHere"
keywords = [
    "星痕共鸣",
    "your-keyword",
]
```

## First Run

The first run will:
1. Search GitHub for each keyword
2. Save all found repositories to `data/`
3. Create an empty RSS feed (no new repos yet)

## Subsequent Runs

Each subsequent run will:
1. Find new repositories since last run
2. Add only new repositories to RSS feed
3. Update the tracking data

## Automation

### Local (cron)
```bash
0 0 * * * cd /path/to/GithubKeyWordMonitor && uv run main.py
```

### GitHub Actions
1. Add `GH_MONITOR_TOKEN` secret to your repository
2. The workflow runs automatically daily at 00:00 UTC
3. Or trigger manually from Actions tab

## Output Files

- `feed.xml` - RSS feed (subscribe to this)
- `data/*.json` - Tracking data (one file per keyword)

## Troubleshooting

**Error: config.toml not found**
- Run: `cp config.toml.example config.toml`
- Edit the file with your token and keywords

**Error: 403 Forbidden**
- Check your GitHub token is valid
- Ensure token has required permissions
- Check API rate limits

**No new repositories found**
- Normal if all repos were seen in previous run
- RSS feed won't be updated if no new repos

**Chinese characters not working**
- Ensure files are saved in UTF-8 encoding
- The code fully supports Unicode keywords
