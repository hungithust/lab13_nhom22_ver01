import argparse
import concurrent.futures
import json
import sys
import time
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")


def get_client() -> httpx.Client | TestClient:
    try:
        httpx.get(f"{BASE_URL}/health", timeout=2.0)
        return httpx.Client(timeout=30.0)
    except Exception:
        return TestClient(app)


def send_request(client: httpx.Client | TestClient, payload: dict) -> None:
    try:
        start = time.perf_counter()
        url = f"{BASE_URL}/chat" if isinstance(client, httpx.Client) else "/chat"
        r = client.post(url, json=payload)
        latency = (time.perf_counter() - start) * 1000
        print(f"[{r.status_code}] {r.json().get('correlation_id')} | {payload['feature']} | {latency:.1f}ms")
    except Exception as e:
        print(f"Error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    args = parser.parse_args()

    lines = [line for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]
    
    with get_client() as client:
        if args.concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = [executor.submit(send_request, client, json.loads(line)) for line in lines]
                concurrent.futures.wait(futures)
        else:
            for line in lines:
                send_request(client, json.loads(line))


if __name__ == "__main__":
    main()
