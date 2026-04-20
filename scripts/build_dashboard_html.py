from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_PATH = ROOT / "data" / "exported_metrics.json"
OUTPUT_PATH = ROOT / "docs" / "dashboard.html"


def format_number(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def build_html(metrics: dict) -> str:
    traffic = int(metrics.get("traffic", 0))
    latency_p50 = float(metrics.get("latency_p50", 0.0))
    latency_p95 = float(metrics.get("latency_p95", 0.0))
    latency_p99 = float(metrics.get("latency_p99", 0.0))
    avg_cost = float(metrics.get("avg_cost_usd", 0.0))
    total_cost = float(metrics.get("total_cost_usd", 0.0))
    tokens_in = int(metrics.get("tokens_in_total", 0))
    tokens_out = int(metrics.get("tokens_out_total", 0))
    quality = float(metrics.get("quality_avg", 0.0))
    error_breakdown = metrics.get("error_breakdown", {})
    error_total = sum(int(v) for v in error_breakdown.values())
    error_rate = (error_total / traffic * 100) if traffic else 0.0
    token_max = max(tokens_in, tokens_out, 1)

    latency_bars = [
        ("P50", latency_p50, "#177f6b"),
        ("P95", latency_p95, "#d97706"),
        ("P99", latency_p99, "#c2410c"),
    ]

    latency_rows = "\n".join(
        f"""
        <div class="bar-row">
          <span>{label}</span>
          <div class="bar-track"><div class="bar-fill" style="width:{min((value / 5000) * 100, 100):.2f}%;background:{color}"></div></div>
          <strong>{format_number(value)} ms</strong>
        </div>
        """
        for label, value, color in latency_bars
    )

    error_items = (
        "".join(f"<li><span>{name}</span><strong>{count}</strong></li>" for name, count in error_breakdown.items())
        if error_breakdown
        else "<li><span>No captured errors</span><strong>0</strong></li>"
    )

    updated_json = json.dumps(metrics, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Day 13 Observability Dashboard</title>
  <style>
    :root {{
      --bg: #f6f1e8;
      --ink: #132a2a;
      --muted: #5a6b67;
      --card: rgba(255,255,255,0.72);
      --line: rgba(19,42,42,0.12);
      --teal: #177f6b;
      --amber: #d97706;
      --red: #c2410c;
      --gold: #b8891d;
      --shadow: 0 18px 45px rgba(19,42,42,0.10);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(23,127,107,0.16), transparent 30%),
        radial-gradient(circle at top right, rgba(184,137,29,0.18), transparent 35%),
        linear-gradient(180deg, #faf6ef 0%, var(--bg) 100%);
      min-height: 100vh;
    }}

    .shell {{
      width: min(1200px, calc(100% - 32px));
      margin: 32px auto;
    }}

    .hero {{
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: linear-gradient(135deg, rgba(255,255,255,0.78), rgba(255,248,235,0.88));
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }}

    .eyebrow {{
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 10px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.4rem);
      line-height: 0.95;
    }}

    .subtitle {{
      margin: 14px 0 0;
      color: var(--muted);
      max-width: 760px;
      font-size: 1rem;
    }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-top: 22px;
    }}

    .summary-card, .panel {{
      border: 1px solid var(--line);
      border-radius: 22px;
      background: var(--card);
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }}

    .summary-card {{
      padding: 18px 20px;
    }}

    .summary-card span {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
    }}

    .summary-card strong {{
      display: block;
      margin-top: 8px;
      font-size: 2rem;
      font-weight: 700;
    }}

    .grid {{
      margin-top: 24px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}

    .panel {{
      padding: 22px;
      overflow: hidden;
      position: relative;
    }}

    .panel::after {{
      content: "";
      position: absolute;
      inset: auto -20% -45% auto;
      width: 180px;
      height: 180px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(23,127,107,0.16), transparent 70%);
      pointer-events: none;
    }}

    .panel h2 {{
      margin: 0 0 6px;
      font-size: 1.2rem;
    }}

    .panel p {{
      margin: 0;
      color: var(--muted);
      font-size: 0.94rem;
    }}

    .stat {{
      margin-top: 18px;
      font-size: 2.6rem;
      font-weight: 700;
    }}

    .mini {{
      font-size: 0.98rem;
      color: var(--muted);
    }}

    .bar-stack {{
      margin-top: 18px;
      display: grid;
      gap: 14px;
    }}

    .bar-row {{
      display: grid;
      grid-template-columns: 48px 1fr auto;
      gap: 12px;
      align-items: center;
    }}

    .bar-track {{
      width: 100%;
      height: 12px;
      border-radius: 999px;
      background: rgba(19,42,42,0.08);
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      border-radius: inherit;
    }}

    .threshold {{
      margin-top: 14px;
      display: flex;
      justify-content: space-between;
      color: var(--muted);
      font-size: 0.88rem;
    }}

    .split {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-top: 18px;
    }}

    .stack-label {{
      font-size: 0.9rem;
      color: var(--muted);
      margin-bottom: 8px;
    }}

    .token-card {{
      padding: 14px;
      border-radius: 18px;
      background: rgba(255,255,255,0.66);
      border: 1px solid rgba(19,42,42,0.08);
    }}

    .token-bar {{
      margin-top: 10px;
      height: 14px;
      border-radius: 999px;
      background: rgba(19,42,42,0.08);
      overflow: hidden;
    }}

    .token-bar > div {{
      height: 100%;
      border-radius: inherit;
    }}

    ul {{
      list-style: none;
      padding: 0;
      margin: 16px 0 0;
      display: grid;
      gap: 10px;
    }}

    li {{
      display: flex;
      justify-content: space-between;
      padding-bottom: 10px;
      border-bottom: 1px dashed rgba(19,42,42,0.10);
    }}

    pre {{
      margin: 18px 0 0;
      padding: 16px;
      border-radius: 18px;
      background: #132a2a;
      color: #f6f1e8;
      overflow: auto;
      font-size: 0.82rem;
    }}

    @media (max-width: 860px) {{
      .summary, .grid, .split {{
        grid-template-columns: 1fr;
      }}
      .shell {{
        width: min(100% - 20px, 1200px);
        margin: 20px auto;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="eyebrow">Observability Layer 2</div>
      <h1>Day 13 HTML Dashboard</h1>
      <p class="subtitle">A standalone 6-panel snapshot built from exported metrics. The layout highlights latency, traffic, errors, cost, token volume, and quality with the same thresholds defined in the lab.</p>
      <div class="summary">
        <article class="summary-card">
          <span>Total Requests</span>
          <strong>{traffic}</strong>
        </article>
        <article class="summary-card">
          <span>Total Cost</span>
          <strong>${format_number(total_cost, 4)}</strong>
        </article>
        <article class="summary-card">
          <span>Quality Average</span>
          <strong>{format_number(quality, 3)}</strong>
        </article>
      </div>
    </section>

    <section class="grid">
      <article class="panel">
        <h2>1. Latency P50 / P95 / P99</h2>
        <p>Tail latency against the lab SLO and alert threshold.</p>
        <div class="bar-stack">{latency_rows}</div>
        <div class="threshold">
          <span>SLO: 3000 ms</span>
          <span>Alert: 5000 ms</span>
        </div>
      </article>

      <article class="panel">
        <h2>2. Traffic</h2>
        <p>Request volume from the exported batch.</p>
        <div class="stat">{traffic}</div>
        <div class="mini">requests in the current snapshot</div>
      </article>

      <article class="panel">
        <h2>3. Error Rate</h2>
        <p>Error percentage with breakdown by error type.</p>
        <div class="stat">{format_number(error_rate)}%</div>
        <div class="mini">alert threshold: 5%</div>
        <ul>{error_items}</ul>
      </article>

      <article class="panel">
        <h2>4. Cost Over Time</h2>
        <p>Average and total cost from the exported metrics set.</p>
        <div class="split">
          <div class="token-card">
            <div class="stack-label">Average Cost / Request</div>
            <strong>${format_number(avg_cost, 4)}</strong>
          </div>
          <div class="token-card">
            <div class="stack-label">Total Cost</div>
            <strong>${format_number(total_cost, 4)}</strong>
          </div>
        </div>
      </article>

      <article class="panel">
        <h2>5. Tokens In / Out</h2>
        <p>Token distribution across the captured requests.</p>
        <div class="split">
          <div class="token-card">
            <div class="stack-label">Tokens In</div>
            <strong>{tokens_in}</strong>
            <div class="token-bar"><div style="width:{(tokens_in / token_max) * 100:.2f}%;background:var(--teal)"></div></div>
          </div>
          <div class="token-card">
            <div class="stack-label">Tokens Out</div>
            <strong>{tokens_out}</strong>
            <div class="token-bar"><div style="width:{(tokens_out / token_max) * 100:.2f}%;background:var(--gold)"></div></div>
          </div>
        </div>
      </article>

      <article class="panel">
        <h2>6. Quality Proxy</h2>
        <p>Heuristic quality score compared with SLO and alert thresholds.</p>
        <div class="stat">{format_number(quality, 3)}</div>
        <div class="mini">SLO minimum: 0.75 | alert minimum: 0.60</div>
      </article>
    </section>

    <section class="panel" style="margin-top:18px;">
      <h2>Exported Metrics Snapshot</h2>
      <p>Embedded source data for auditability.</p>
      <pre>{updated_json}</pre>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    exported = json.loads(EXPORT_PATH.read_text(encoding="utf-8"))
    metrics = exported.get("metrics", {})
    OUTPUT_PATH.write_text(build_html(metrics), encoding="utf-8")
    print(f"Built HTML dashboard at {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
