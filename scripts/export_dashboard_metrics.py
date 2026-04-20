from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean

import httpx
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from app.metrics import percentile

BASE_URL = "http://127.0.0.1:8000"
EXPORT_PATH = Path("data/exported_metrics.json")
DASHBOARD_PATH = Path("docs/dashboard.json")
LOG_PATH = Path("data/logs.jsonl")


def build_panels(metrics: dict) -> list[dict]:
    error_breakdown = metrics.get("error_breakdown", {})
    total_errors = sum(error_breakdown.values())
    traffic = metrics.get("traffic", 0)
    error_rate_pct = round((total_errors / traffic) * 100, 2) if traffic else 0.0

    return [
        {
            "title": "Latency P50/P95/P99",
            "unit": "ms",
            "visualization": "timeseries",
            "values": {
                "p50": metrics.get("latency_p50", 0.0),
                "p95": metrics.get("latency_p95", 0.0),
                "p99": metrics.get("latency_p99", 0.0),
            },
            "thresholds": {"slo_ms": 3000, "alert_ms": 5000},
        },
        {
            "title": "Traffic",
            "unit": "requests",
            "visualization": "stat",
            "values": {"total_requests": traffic},
        },
        {
            "title": "Error Rate",
            "unit": "percent",
            "visualization": "stat",
            "values": {"error_rate_pct": error_rate_pct, "breakdown": error_breakdown},
            "thresholds": {"alert_pct": 5},
        },
        {
            "title": "Cost Over Time",
            "unit": "usd",
            "visualization": "stat",
            "values": {
                "avg_cost_usd": metrics.get("avg_cost_usd", 0.0),
                "total_cost_usd": metrics.get("total_cost_usd", 0.0),
            },
        },
        {
            "title": "Tokens In/Out",
            "unit": "tokens",
            "visualization": "bargauge",
            "values": {
                "tokens_in_total": metrics.get("tokens_in_total", 0),
                "tokens_out_total": metrics.get("tokens_out_total", 0),
            },
        },
        {
            "title": "Quality Proxy",
            "unit": "score",
            "visualization": "stat",
            "values": {"quality_avg": metrics.get("quality_avg", 0.0)},
            "thresholds": {"slo_min": 0.75, "alert_min": 0.6},
        },
    ]


def get_metrics() -> dict:
    try:
        response = httpx.get(f"{BASE_URL}/metrics", timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        with TestClient(app) as client:
            response = client.get("/metrics")
            metrics = response.json()
        if metrics.get("traffic"):
            return metrics
        return derive_metrics_from_logs()


def derive_metrics_from_logs() -> dict:
    records = [json.loads(line) for line in LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    responses = [rec for rec in records if rec.get("event") == "response_sent"]
    failures = [rec for rec in records if rec.get("event") == "request_failed"]

    latencies = [int(rec.get("latency_ms", 0)) for rec in responses]
    costs = [float(rec.get("cost_usd", 0.0)) for rec in responses]
    tokens_in = [int(rec.get("tokens_in", 0)) for rec in responses]
    tokens_out = [int(rec.get("tokens_out", 0)) for rec in responses]
    quality_scores = [float(rec.get("quality_score", 0.0)) for rec in responses if "quality_score" in rec]

    error_breakdown: dict[str, int] = {}
    for rec in failures:
        error_type = str(rec.get("error_type", "unknown"))
        error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1

    return {
        "traffic": len(responses),
        "latency_p50": percentile(latencies, 50),
        "latency_p95": percentile(latencies, 95),
        "latency_p99": percentile(latencies, 99),
        "avg_cost_usd": round(mean(costs), 4) if costs else 0.0,
        "total_cost_usd": round(sum(costs), 4),
        "tokens_in_total": sum(tokens_in),
        "tokens_out_total": sum(tokens_out),
        "error_breakdown": error_breakdown,
        "quality_avg": round(mean(quality_scores), 4) if quality_scores else 0.0,
    }


def main() -> None:
    metrics = get_metrics()
    export = {"source": f"{BASE_URL}/metrics", "metrics": metrics}
    dashboard = {
        "title": "Day 13 Observability Dashboard",
        "refresh_seconds": 15,
        "time_range": "last_1_hour",
        "panels": build_panels(metrics),
    }

    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_PATH.write_text(json.dumps(export, indent=2), encoding="utf-8")
    DASHBOARD_PATH.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")

    print(f"Exported metrics to {EXPORT_PATH}")
    print(f"Built dashboard definition at {DASHBOARD_PATH}")


if __name__ == "__main__":
    main()
