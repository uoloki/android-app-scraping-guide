# 4. Export the captured API with Python

[Previous: discover the API](03-api-discovery.md) · [Next: advanced setup](05-dual-emulator-apks.md)

The [included exporter](../scraper/main.py) calls the two requests identified in the capture. It needs neither the emulator nor the proxy once you know the public API path.

From this guide's root folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\scraper\requirements.txt
.\.venv\Scripts\python.exe .\scraper\main.py --query phone --max-items 40 --format csv --output .\phones.csv
```

Open `phones.csv`. Each row is a product; `id`, `title`, `price`, and other fields come from the JSON response. The capture had 23 `phone` matches, but the live total may change.

To export the first five products as JSON and fetch each product's detail endpoint:

```powershell
.\.venv\Scripts\python.exe .\scraper\main.py --max-items 5 --details --format json --output .\products.json
```

The exporter sends `q`, `skip`, and `limit` as captured. It advances `skip` by the returned product count and stops at `total`, an empty page, or `--max-items`. It uses timeouts, bounded retries, and a short delay between requests. It never needs a token for this public demo.

Run the small offline test suite:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s .\scraper\tests -v
```

Compare the exported product IDs with the captured responses. The [sanitized fixtures](../examples/sanitized-responses/) show the expected JSON shape. For another authorized app, map its screens to requests before changing the exporter's URL, parameters, and response fields.
