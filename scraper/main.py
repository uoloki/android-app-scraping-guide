"""Export products from the JSON API observed in the demo Android app.

Examples:
    python main.py --query phone --max-items 40 --format csv --output phones.csv
    python main.py --details --max-items 5 --output products.json
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from typing import Any, Callable, Iterator

import requests


BASE_URL = "https://dummyjson.com"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


@dataclass(frozen=True)
class Product:
    id: int
    title: str
    description: str | None
    category: str | None
    price: float | None
    discount_percentage: float | None
    rating: float | None
    stock: int | None
    brand: str | None
    sku: str | None
    thumbnail: str | None
    images: list[str]

    @classmethod
    def from_api(cls, value: dict[str, Any]) -> "Product":
        return cls(
            id=int(value["id"]),
            title=str(value["title"]),
            description=value.get("description"),
            category=value.get("category"),
            price=value.get("price"),
            discount_percentage=value.get("discountPercentage"),
            rating=value.get("rating"),
            stock=value.get("stock"),
            brand=value.get("brand"),
            sku=value.get("sku"),
            thumbnail=value.get("thumbnail"),
            images=value.get("images") or [],
        )


class ProductClient:
    def __init__(
        self,
        *,
        base_url: str = BASE_URL,
        timeout: float = 10.0,
        retries: int = 3,
        delay: float = 0.25,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        if timeout <= 0 or retries < 0 or delay < 0:
            raise ValueError("timeout must be positive; retries and delay must be nonnegative")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.delay = delay
        self.session = session or requests.Session()
        self._sleep = sleep
        self._monotonic = monotonic
        self._last_request: float | None = None
        self.session.headers.update({"User-Agent": "android-app-scraping-guide/1.0"})

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(self.retries + 1):
            if self._last_request is not None:
                remaining = self.delay - (self._monotonic() - self._last_request)
                if remaining > 0:
                    self._sleep(remaining)
            self._last_request = self._monotonic()
            try:
                response = self.session.get(
                    f"{self.base_url}{path}", params=params, timeout=self.timeout
                )
                if response.status_code in RETRYABLE_STATUS and attempt < self.retries:
                    retry_after = response.headers.get("Retry-After", "")
                    try:
                        wait = max(0.0, float(retry_after))
                    except ValueError:
                        wait = min(2**attempt, 30.0)
                    response.close()
                    self._sleep(wait)
                    continue
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise ValueError(f"Expected a JSON object from {path}")
                return data
            except (requests.ConnectionError, requests.Timeout):
                if attempt == self.retries:
                    raise
                self._sleep(min(2**attempt, 30.0))
        raise AssertionError("unreachable")

    def search(
        self, query: str = "", *, page_size: int = 20, max_items: int | None = None
    ) -> Iterator[Product]:
        if page_size <= 0 or max_items is not None and max_items < 0:
            raise ValueError("page_size must be positive and max_items nonnegative")
        skip = 0
        yielded = 0
        while max_items is None or yielded < max_items:
            limit = min(page_size, max_items - yielded) if max_items is not None else page_size
            data = self._get(
                "/products/search", {"skip": skip, "limit": limit, "q": query}
            )
            products = data.get("products")
            if not isinstance(products, list):
                raise ValueError("Search response has no products list")
            for item in products:
                yield Product.from_api(item)
                yielded += 1
            skip += len(products)
            if not products or skip >= int(data["total"]):
                break

    def detail(self, product_id: int) -> Product:
        if product_id <= 0:
            raise ValueError("product_id must be positive")
        return Product.from_api(self._get(f"/products/{product_id}"))


def export(products: list[Product], path: Path, format: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        payload = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "count": len(products),
            "products": [asdict(product) for product in products],
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    elif format == "csv":
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=[field.name for field in fields(Product)])
            writer.writeheader()
            for product in products:
                row = asdict(product)
                row["images"] = json.dumps(row["images"], ensure_ascii=False)
                writer.writerow(row)
    else:
        raise ValueError(f"Unsupported format: {format}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="Search term (empty returns all products)")
    parser.add_argument("--page-size", type=int, default=20)
    parser.add_argument("--max-items", type=int, default=None)
    parser.add_argument("--details", action="store_true", help="Fetch each product detail endpoint")
    parser.add_argument("--timeout", type=float, default=10.0, help="Seconds per request")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.25, help="Minimum seconds between requests")
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--output", type=Path, help="Output file (defaults to products.json/csv)")
    args = parser.parse_args(argv)
    try:
        client = ProductClient(timeout=args.timeout, retries=args.retries, delay=args.delay)
        products = list(client.search(args.query, page_size=args.page_size, max_items=args.max_items))
        if args.details:
            products = [client.detail(product.id) for product in products]
        path = args.output or Path(f"products.{args.format}")
        export(products, path, args.format)
    except (ValueError, KeyError, requests.RequestException, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Exported {len(products)} products to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
