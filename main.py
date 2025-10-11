import json
import logging
import tomllib
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from feedgen.feed import FeedGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
CONFIG_FILE = Path("config.toml")
DATA_DIR = Path("data")
FEED_FILE = Path("feed.xml")
FEEDS_DIR = Path("feeds")
GITHUB_API_BASE = "https://api.github.com"


def load_config() -> dict[str, Any]:
    """Load configuration from config.toml."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"{CONFIG_FILE} not found. Please copy config.toml.example to config.toml and configure it."
        )
    
    with open(CONFIG_FILE, "rb") as f:
        config = tomllib.load(f)
    
    if not config.get("github_token"):
        raise ValueError("github_token is required in config.toml")
    
    if not config.get("keywords"):
        raise ValueError("keywords list is required in config.toml")
    
    return config


def load_seen_repos(keyword: str) -> set[str]:
    """Load the set of repository full names that have been seen for a keyword."""
    data_file = DATA_DIR / f"{quote(keyword, safe='')}.json"
    if not data_file.exists():
        return set()
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return set(data.get("seen_repos", []))


def save_seen_repos(keyword: str, seen_repos: set[str]) -> None:
    """Save the set of repository full names that have been seen for a keyword."""
    DATA_DIR.mkdir(exist_ok=True)
    data_file = DATA_DIR / f"{quote(keyword, safe='')}.json"
    
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump({"seen_repos": list(seen_repos)}, f, ensure_ascii=False, indent=2)


def keyword_matches(keyword: str, text: str | None) -> bool:
    """Check if keyword matches text (case-insensitive for English)."""
    if text is None:
        return False
    
    # For case-insensitive matching
    return keyword.lower() in text.lower()


def search_github_repos(
    keyword: str, 
    github_token: str
) -> list[dict[str, Any]]:
    """
    Search GitHub repositories by keyword.
    
    Returns repositories sorted by updated date (descending).
    Results are filtered to ensure the keyword appears in name or description.
    """
    encoded_keyword = quote(keyword)
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {
        "q": keyword,
        "sort": "updated",
        "order": "desc",
        "per_page": 100,
    }
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Filter results to ensure keyword is in name or description
        repos = []
        for repo in data.get("items", []):
            repo_name = repo.get("name", "")
            repo_full_name = repo.get("full_name", "")
            repo_description = repo.get("description")
            
            # Check if keyword appears in name or description
            if keyword_matches(keyword, repo_name) or keyword_matches(keyword, repo_description):
                repos.append(repo)
        
        logger.info(f"Found {len(repos)} repositories matching keyword '{keyword}' on this page (filtered from {data.get('total_count', 0)} total results across all pages)")
        return repos
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching GitHub for keyword '{keyword}': {e}")
        return []


def _create_feed_generator(keyword: str | None = None) -> FeedGenerator:
    """Create a FeedGenerator configured for the aggregate feed or a specific keyword."""
    fg = FeedGenerator()

    base_id = "https://github.com/233Official/GithubKeyWordMonitor"
    base_title = "GitHub Keyword Monitor"
    base_description = "Monitor GitHub repositories by keywords"

    if keyword is None:
        fg.id(base_id)
        fg.title(base_title)
        fg.description(base_description)
    else:
        encoded_keyword = quote(keyword, safe="")
        fg.id(f"{base_id}?keyword={encoded_keyword}")
        fg.title(f"{base_title} - {keyword}")
        fg.description(f"Monitor GitHub repositories for keyword '{keyword}'")

    fg.link(href="https://github.com/233Official/GithubKeyWordMonitor", rel="alternate")
    fg.language("en")
    return fg


def _add_repo_entry_to_feed(
    fg: FeedGenerator,
    repo: dict[str, Any],
    keyword: str,
    *,
    include_keyword_prefix: bool,
) -> None:
    """Add a repository entry to the given feed."""
    fe = fg.add_entry()
    fe.id(repo["html_url"])

    title = repo["full_name"]
    if include_keyword_prefix:
        title = f"[{keyword}] {title}"
    fe.title(title)
    fe.link(href=repo["html_url"])

    plain_description_parts = []
    repo_description = repo.get("description")
    if repo_description:
        plain_description_parts.append(repo_description)

    plain_description_parts.extend(
        [
            f"Stars: {repo.get('stargazers_count', 0)}",
            f"Language: {repo.get('language') or 'N/A'}",
            f"Updated: {repo.get('updated_at') or 'N/A'}",
        ]
    )

    fe.description("\n".join(plain_description_parts))

    description_segments: list[str] = []
    if repo_description:
        description_segments.append(f"<p>{escape(repo_description)}</p>")

    metadata_items = [
        ("Stars", repo.get("stargazers_count", 0)),
        ("Language", repo.get("language") or "N/A"),
        ("Updated", repo.get("updated_at") or "N/A"),
    ]

    metadata_html = "".join(
        f"<li><strong>{label}:</strong> {escape(str(value))}</li>"
        for label, value in metadata_items
    )
    description_segments.append(f"<ul>{metadata_html}</ul>")

    fe.content("".join(description_segments), type="CDATA")

    updated_at = repo.get("updated_at")
    if updated_at:
        fe.published(updated_at)
        fe.updated(updated_at)


def generate_rss_feeds(all_new_repos: dict[str, list[dict[str, Any]]]) -> None:
    """Generate aggregate and per-keyword RSS feeds from new repositories."""
    aggregate_feed = _create_feed_generator()
    keyword_feeds: dict[str, FeedGenerator] = {}

    total_entries = 0

    for keyword, repos in all_new_repos.items():
        if not repos:
            continue

        keyword_feed = _create_feed_generator(keyword)
        keyword_entries = 0

        for repo in repos:
            _add_repo_entry_to_feed(
                aggregate_feed,
                repo,
                keyword,
                include_keyword_prefix=True,
            )
            _add_repo_entry_to_feed(
                keyword_feed,
                repo,
                keyword,
                include_keyword_prefix=False,
            )
            total_entries += 1
            keyword_entries += 1

        if keyword_entries:
            keyword_feeds[keyword] = keyword_feed

    if not total_entries:
        logger.info("No RSS entries to generate")
        return

    aggregate_feed.rss_file(str(FEED_FILE), pretty=True)
    logger.info(f"RSS feed generated: {FEED_FILE}")

    if keyword_feeds:
        FEEDS_DIR.mkdir(exist_ok=True)
        for keyword, fg in keyword_feeds.items():
            file_path = FEEDS_DIR / f"{quote(keyword, safe='')}.xml"
            fg.rss_file(str(file_path), pretty=True)
            logger.info(f"RSS feed generated for keyword '{keyword}': {file_path}")


def main():
    """Main entry point."""
    logger.info("Starting GitHub Keyword Monitor")
    
    # Load configuration
    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Configuration error: {e}")
        return
    
    github_token = config["github_token"]
    keywords = config["keywords"]
    
    # Track all new repositories across all keywords
    all_new_repos: dict[str, list[dict[str, Any]]] = {}
    
    # Process each keyword
    for keyword in keywords:
        logger.info(f"Processing keyword: {keyword}")
        
        # Load previously seen repositories
        seen_repos = load_seen_repos(keyword)
        logger.info(f"Previously seen {len(seen_repos)} repositories for keyword '{keyword}'")
        
        # Search GitHub
        repos = search_github_repos(keyword, github_token)
        
        # Find new repositories
        new_repos = []
        current_repos = set()
        
        for repo in repos:
            full_name = repo["full_name"]
            current_repos.add(full_name)
            
            if full_name not in seen_repos:
                new_repos.append(repo)
                logger.info(f"New repository found: {full_name}")
        
        if new_repos:
            all_new_repos[keyword] = new_repos
        
        # Update seen repositories
        save_seen_repos(keyword, current_repos)
    
    # Generate RSS feed if there are new repositories
    if all_new_repos:
        total_new = sum(len(repos) for repos in all_new_repos.values())
        logger.info(f"Found {total_new} new repositories across all keywords")
        generate_rss_feeds(all_new_repos)
    else:
        logger.info("No new repositories found")
    
    logger.info("GitHub Keyword Monitor completed")


if __name__ == "__main__":
    main()
