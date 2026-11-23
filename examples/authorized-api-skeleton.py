"""Replay one authorized, read-only app request.

Set APP_API_BASE_URL, APP_READ_PATH, and APP_ACCESS_TOKEN from your own
permitted test session. APP_QUERY_JSON is optional, for observed parameters.
"""
import json
import os
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

import httpx


def main():
    base = os.environ["APP_API_BASE_URL"].rstrip("/")
    path = os.environ["APP_READ_PATH"]
    token = os.environ["APP_ACCESS_TOKEN"]
    params = json.loads(os.getenv("APP_QUERY_JSON", "{}"))

    if (urlsplit(base).scheme != "https" or not urlsplit(base).netloc
            or not path.startswith("/") or "//" in path):
        raise ValueError("Use an HTTPS base URL and a relative path beginning with /")
    if not isinstance(params, dict):
        raise ValueError("APP_QUERY_JSON must contain a JSON object")

    with httpx.Client(
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=15.0,
        follow_redirects=False,
    ) as client:
        for attempt in range(3):
            response = client.get(base + path, params=params)
            if response.status_code in (401, 403):
                raise RuntimeError("Session is expired or outside its allowed scope")
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "2")
                try:
                    delay = float(retry_after)
                except ValueError:
                    try:
                        delay = (parsedate_to_datetime(retry_after)
                                 - datetime.now(timezone.utc)).total_seconds()
                    except (TypeError, ValueError):
                        delay = 2
                delay = min(max(delay, 0), 30)
                time.sleep(delay)
                continue
            if response.status_code >= 500 and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            body = response.json()
            print("HTTP", response.status_code)
            print("JSON keys:", list(body) if isinstance(body, dict) else type(body).__name__)
            return
        raise RuntimeError("Request was rate limited after bounded retries")


if __name__ == "__main__":
    main()
