# From Android screen to Python scraper

A visual, tested walkthrough: capture an Android app's HTTPS requests with mitmproxy, find the API behind each screen, and export the data with Python. It uses an [open-source shopping app](https://github.com/Hasuk1/dummyjson_products) and the public [DummyJSON](https://dummyjson.com/docs/products) API, then covers Play services, Magisk root, system CA trust, and certificate pinning.

**Read the guide online:** https://uoloki.github.io/android-app-scraping-guide/ (or browse [docs/index.md](docs/index.md) on GitHub).

## What's in the repository

| Folder | Contents |
| --- | --- |
| `docs/` | The guide chapters and screenshots |
| `scraper/` | The DummyJSON exporter and its offline tests |
| `examples/` | Sanitized API responses, the Frida hook, and a read-only API skeleton |

## Run the exporter

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\scraper\requirements.txt
.\.venv\Scripts\python.exe .\scraper\main.py --query phone --max-items 40 --format csv --output .\phones.csv
```

## Preview the docs site locally

```powershell
python -m pip install -r requirements-docs.txt
mkdocs serve
```

Then open `http://127.0.0.1:8000`. Pushing to `main` publishes the site through GitHub Actions.

Work only with apps and services you are authorized to inspect.

## License

The code in `scraper/`, `examples/`, and `hooks/` is under the [MIT License](LICENSE). The guide text and screenshots in `docs/` are under [CC BY-NC 4.0](LICENSE-docs.md): free to share and adapt for non-commercial use with credit.

