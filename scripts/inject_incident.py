from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app

BASE_URL = "http://127.0.0.1:8000"


def post(path: str):
    try:
        return httpx.post(f"{BASE_URL}{path}", timeout=10.0)
    except Exception:
        with TestClient(app) as client:
            return client.post(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, choices=["rag_slow", "tool_fail", "cost_spike"])
    parser.add_argument("--disable", action="store_true")
    args = parser.parse_args()

    path = f"/incidents/{args.scenario}/disable" if args.disable else f"/incidents/{args.scenario}/enable"
    r = post(path)
    print(r.status_code, r.json())


if __name__ == "__main__":
    main()
