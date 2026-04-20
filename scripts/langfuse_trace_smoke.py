from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")


def load_payloads(limit: int) -> list[dict]:
    rows = [json.loads(line) for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise RuntimeError("No sample queries found in data/sample_queries.jsonl")

    payloads: list[dict] = []
    while len(payloads) < limit:
        for row in rows:
            if len(payloads) >= limit:
                break
            idx = len(payloads) + 1
            payload = dict(row)
            payload["session_id"] = f"{row['session_id']}-trace-{idx:02d}"
            payloads.append(payload)
    return payloads


def get_client() -> httpx.Client | TestClient:
    try:
        httpx.get(f"{BASE_URL}/health", timeout=2.0)
        return httpx.Client(timeout=30.0)
    except Exception:
        return TestClient(app)


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a batch of requests for Langfuse trace verification.")
    parser.add_argument("--count", type=int, default=12, help="How many requests to send (recommended: 10-20)")
    args = parser.parse_args()

    payloads = load_payloads(args.count)
    correlation_ids: list[str] = []

    with get_client() as client:
        for index, payload in enumerate(payloads, start=1):
            url = f"{BASE_URL}/chat" if isinstance(client, httpx.Client) else "/chat"
            response = client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
            correlation_id = body.get("correlation_id", "missing")
            correlation_ids.append(correlation_id)
            print(f"{index:02d}. {correlation_id} | {payload['session_id']} | {payload['feature']}")

    print(f"Sent {len(payloads)} requests.")
    print(f"Unique correlation IDs: {len(set(correlation_ids))}")


if __name__ == "__main__":
    main()
