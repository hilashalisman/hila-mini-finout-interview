"""The customer-facing app, mock edition. Runs two servers side by side:

    python app/serve.py

    http://localhost:8080          the dashboard, which charts the pipeline's output
    http://localhost:8081/usage    Acme's Anthropic usage API, a source the pipeline fetches from

The pipeline's output is every CSV under s3-storage-mock/output/, header
date,source,team,service,cost. Every dashboard request re-reads it, so re-running the pipeline and
refreshing the page is enough to see the new numbers. Standard library only - nothing to install.

output/example.csv is fake sample data. It is shown only while it is the only CSV there, and
ignored as soon as the pipeline writes its own.
"""
import csv
import json
import random
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

APP_DIR = Path(__file__).resolve().parent
REPO_DIR = APP_DIR.parent
PORT = 8080
USAGE_API_PORT = 8081
USAGE_DATA_PATH = APP_DIR / "mock_api" / "usage.json"
USAGE_API_FAILURE_RATE = 1 / 50
OUTPUT_DIR = REPO_DIR / "s3-storage-mock" / "output"
OUTPUT_COLUMNS = ["date", "source", "team", "service", "cost"]
EXAMPLE_OUTPUT_FILE = OUTPUT_DIR / "example.csv"


def find_output_files() -> tuple[list[Path], bool]:
    """The pipeline's CSVs under the output folder, at any depth - or the example, while alone."""
    all_files = sorted(OUTPUT_DIR.rglob("*.csv"))
    pipeline_files = [path for path in all_files if path != EXAMPLE_OUTPUT_FILE]
    if pipeline_files:
        return pipeline_files, False
    if EXAMPLE_OUTPUT_FILE.exists():
        return [EXAMPLE_OUTPUT_FILE], True
    raise FileNotFoundError(f"no CSV files under {OUTPUT_DIR.relative_to(REPO_DIR)}/")


def load_unified_data(output_files: list[Path]) -> list[dict[str, Any]]:
    """Every row of the given output CSVs."""
    rows: list[dict[str, Any]] = []
    for output_file in output_files:
        with open(output_file, newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != OUTPUT_COLUMNS:
                expected_header = ",".join(OUTPUT_COLUMNS)
                raise ValueError(f"{output_file.name}: the header must be {expected_header}")
            for row in reader:
                rows.append({**row, "cost": float(row["cost"])})
    return rows


def load_usage_records(day: str) -> list[dict[str, Any]]:
    """The usage API's records for one day, or none if it has no data for that day."""
    usage_by_day: dict[str, list[dict[str, Any]]] = json.loads(USAGE_DATA_PATH.read_text())
    records = usage_by_day.get(day, [])
    return records


def respond_with_json(handler: BaseHTTPRequestHandler, status: int, payload: Any) -> None:
    body = json.dumps(payload, default=str).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


class AppRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path.startswith("/api/unified-data"):
            self._respond_with_unified_data()
        elif self.path.startswith("/mock_api"):
            respond_with_json(self, 404, {"error": "not found"})
        else:
            super().do_GET()

    def _respond_with_unified_data(self) -> None:
        payload: dict[str, Any]
        try:
            output_files, is_example = find_output_files()
            rows = load_unified_data(output_files)
            payload = {"rows": rows, "example": is_example}
            status = 200
        except FileNotFoundError as error:
            payload = {"error": str(error)}
            status = 404
        except ValueError as error:
            payload = {"error": str(error)}
            status = 500
        respond_with_json(self, status, payload)


class UsageApiRequestHandler(BaseHTTPRequestHandler):
    """GET /usage?date=YYYY-MM-DD -> a list of {request_id, timestamp, team, model, tokens}."""

    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path != "/usage":
            respond_with_json(self, 404, {"error": "not found"})
            return
        if random.random() < USAGE_API_FAILURE_RATE:
            respond_with_json(self, 500, {"error": "internal server error"})
            return

        query = parse_qs(url.query)
        day = query.get("date", [""])[0]
        try:
            date.fromisoformat(day)
        except ValueError:
            respond_with_json(self, 400, {"error": "date must be YYYY-MM-DD"})
            return
        records = load_usage_records(day)
        respond_with_json(self, 200, records)


def start_server(port: int, handler: type[BaseHTTPRequestHandler], name: str) -> Optional[HTTPServer]:
    try:
        server = HTTPServer(("", port), handler)
    except OSError:
        print(f"{name} is already running on http://localhost:{port}")
        return None
    print(f"{name}: http://localhost:{port}")
    return server


def main() -> None:
    app_server = start_server(PORT, AppRequestHandler, "mini-finout app")
    usage_api_server = start_server(USAGE_API_PORT, UsageApiRequestHandler, "acme usage api")
    servers = [server for server in [app_server, usage_api_server] if server is not None]
    threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in servers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
