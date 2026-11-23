"""Point links to code outside docs/ (scraper/, examples/) at the GitHub repository.

The pages link to ../scraper/... and ../examples/... so they also work when browsing
the repository on GitHub. MkDocs only publishes docs/, so on the site those links
become GitHub URLs built from repo_url. Without repo_url they are left unchanged.
"""
import re

LINK = re.compile(r"\]\(\.\./((?:scraper|examples)/[^)\s]*)\)")
BRANCH = "main"


def on_page_markdown(markdown, page, config, files):
    repo_url = (config.get("repo_url") or "").rstrip("/")
    if not repo_url:
        return markdown

    def to_github(match):
        path = match.group(1)
        kind = "tree" if path.endswith("/") else "blob"
        return f"]({repo_url}/{kind}/{BRANCH}/{path.rstrip('/')})"

    return LINK.sub(to_github, markdown)
