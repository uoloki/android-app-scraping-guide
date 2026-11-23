import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import Product, ProductClient, export  # noqa: E402


def response(payload, status=200, headers=None):
    result = Mock()
    result.status_code = status
    result.headers = headers or {}
    result.json.return_value = payload
    result.raise_for_status.side_effect = None
    return result


class ProductClientTests(unittest.TestCase):
    def test_search_paginates_and_passes_query(self):
        session = Mock()
        session.headers = {}
        session.get.side_effect = [
            response({"products": [{"id": 1, "title": "A"}, {"id": 2, "title": "B"}], "total": 3}),
            response({"products": [{"id": 3, "title": "C"}], "total": 3}),
        ]
        client = ProductClient(session=session, delay=0)
        products = list(client.search("phone", page_size=2))
        self.assertEqual([product.id for product in products], [1, 2, 3])
        self.assertEqual(session.get.call_args_list[0].kwargs["params"], {"skip": 0, "limit": 2, "q": "phone"})
        self.assertEqual(session.get.call_args_list[1].kwargs["params"], {"skip": 2, "limit": 2, "q": "phone"})

    def test_max_items_and_detail_endpoint(self):
        session = Mock()
        session.headers = {}
        session.get.side_effect = [
            response({"products": [{"id": 7, "title": "Phone"}], "total": 100}),
            response({"id": 7, "title": "Phone", "brand": "Example", "images": ["one.jpg"]}),
        ]
        client = ProductClient(session=session, delay=0)
        product = next(client.search(max_items=1))
        detail = client.detail(product.id)
        self.assertEqual(detail.brand, "Example")
        self.assertEqual(detail.images, ["one.jpg"])
        self.assertEqual(session.get.call_args_list[0].kwargs["params"]["limit"], 1)
        self.assertTrue(session.get.call_args_list[1].args[0].endswith("/products/7"))

    def test_retries_transient_status_and_respects_retry_after(self):
        session = Mock()
        session.headers = {}
        session.get.side_effect = [
            response({}, 429, {"Retry-After": "2"}),
            response({"id": 9, "title": "Camera"}),
        ]
        sleeps = []
        client = ProductClient(session=session, retries=1, delay=0, sleep=sleeps.append)
        self.assertEqual(client.detail(9).id, 9)
        self.assertEqual(sleeps, [2.0])
        self.assertEqual(session.get.call_count, 2)

    def test_exports_json_and_csv(self):
        product = Product.from_api({"id": 1, "title": "Éclair", "images": ["a.jpg", "b.jpg"]})
        with tempfile.TemporaryDirectory() as folder:
            json_path = Path(folder) / "products.json"
            csv_path = Path(folder) / "products.csv"
            export([product], json_path, "json")
            export([product], csv_path, "csv")
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["products"][0]["title"], "Éclair")
            self.assertEqual(payload["count"], 1)
            with csv_path.open(encoding="utf-8-sig", newline="") as file:
                row = next(csv.DictReader(file))
            self.assertEqual(row["title"], "Éclair")
            self.assertEqual(json.loads(row["images"]), ["a.jpg", "b.jpg"])


if __name__ == "__main__":
    unittest.main()
