from .base import safe_get
from typing import Optional
import re


async def collect_github_data(protocol_name: str) -> dict:
    slug = protocol_name.lower().replace(" ", "-").replace(".", "")
    candidates = [slug, f"{slug}-protocol", f"{slug}-labs", f"{slug}-xyz"]

    repo_data = None
    for candidate in candidates:
        data = await safe_get(f"https://api.github.com/repos/{candidate}/{candidate}")
        if data and "full_name" in data:
            repo_data = data
            break
        # Try searching
        search = await safe_get(
            "https://api.github.com/search/repositories",
            params={"q": f"{protocol_name} blockchain", "sort": "stars", "per_page": 3},
        )
        if search and search.get("items"):
            repo_data = search["items"][0]
            break

    if not repo_data:
        return {
            "found": False,
            "protocol": protocol_name,
            "summary": f"No public GitHub repository found for {protocol_name}",
        }

    full_name = repo_data.get("full_name", "")
    commits_data = await safe_get(f"https://api.github.com/repos/{full_name}/commits?per_page=10")
    contributors = await safe_get(f"https://api.github.com/repos/{full_name}/contributors?per_page=10")

    return {
        "found": True,
        "full_name": full_name,
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "open_issues": repo_data.get("open_issues_count", 0),
        "language": repo_data.get("language"),
        "description": repo_data.get("description"),
        "created_at": repo_data.get("created_at"),
        "updated_at": repo_data.get("updated_at"),
        "topics": repo_data.get("topics", []),
        "recent_commits": len(commits_data) if commits_data else 0,
        "contributors_count": len(contributors) if contributors else 0,
        "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
        "is_archived": repo_data.get("archived", False),
        "has_wiki": repo_data.get("has_wiki", False),
    }
