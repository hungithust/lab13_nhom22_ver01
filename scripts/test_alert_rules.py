from __future__ import annotations

import json
import subprocess
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
ALERT_RULES_PATH = Path("config/alert_rules.yaml")


def parse_alerts() -> list[dict[str, str]]:
    alerts: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in ALERT_RULES_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- name:"):
            if current:
                alerts.append(current)
            current = {"name": stripped.split(":", 1)[1].strip()}
            continue

        if current and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip().strip('"')

    if current:
        alerts.append(current)

    return alerts


def run_test_command(command: str) -> dict[str, str | int]:
    completed = subprocess.run(command.split(), capture_output=True, text=True, check=False)
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main() -> None:
    alerts = parse_alerts()
    if not alerts:
        raise RuntimeError("No alerts found in config/alert_rules.yaml")

    health = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    health.raise_for_status()

    results: list[dict[str, object]] = []
    for alert in alerts:
        result: dict[str, object] = {
            "name": alert.get("name", "unknown"),
            "severity": alert.get("severity", ""),
            "condition": alert.get("condition", ""),
            "runbook": alert.get("runbook", ""),
            "has_runbook": bool(alert.get("runbook")),
        }

        command = alert.get("test_command")
        if command:
            command_result = run_test_command(command)
            result["test_command"] = command
            result["test_result"] = command_result

            scenario = command.split()[-1]
            disable_result = run_test_command(f"python scripts/inject_incident.py --scenario {scenario} --disable")
            result["disable_result"] = disable_result

        results.append(result)

    output = {"health": health.json(), "alerts_tested": results}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
