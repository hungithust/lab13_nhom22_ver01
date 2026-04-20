# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: nhóm 22
- [REPO_URL]: https://github.com/your-org/lab13_nhom22_ver01
- [MEMBERS]:
  - Member A: Nguyễn Viết Hùng | Role: Logging & PII
  - Member B: Nguyễn Xuân Tùng | Role: Tracing & Enrichment
  - Member C: Nguyễn Công Thành | Role: SLO & Alerts
  - Member D: Trần Quốc Khánh | Role: Load Test & Dashboard
  - Member E: Đỗ Đình Hoàn | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 30
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: data/logs.jsonl - Lines with req-fab4e22f, req-f55b3587
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: data/logs.jsonl - [REDACTED_EMAIL], [REDACTED_PHONE_VN], [REDACTED_CREDIT_CARD]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: traces/waterfall_req-fab4e22f.png
- [TRACE_WATERFALL_EXPLANATION]: Correlation ID req-fab4e22f demonstrates a complete request-response cycle for a refund policy query. The trace shows: (1) request_received event at 09:53:33.659528Z with user_id_hash 2055254ee30a; (2) processing through API gateway; (3) response_sent event at 09:53:33.812245Z with 150ms latency, tokens processed (37 in, 104 out), and cost tracking (0.001671 USD). All PII (email) was properly redacted in logs.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: dashboard/main-dashboard.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 150ms |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | $0.0635 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: config/alert_rules.yaml
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md](docs/alerts.md)

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: high_pii_exposure
- [SYMPTOMS_OBSERVED]: Unredacted user email addresses appearing in response logs; Potential PII leak detected in message previews during request_received events
- [ROOT_CAUSE_PROVED_BY]: Trace ID req-fab4e22f at timestamp 2026-04-20T09:53:33.659528Z shows message_preview contains "My email is [REDACTED_EMAIL]" - redaction middleware intercepted and masked PII correctly. No actual leaks in system logs.
- [FIX_ACTION]: Verified PII redaction patterns for email, phone (Vietnamese format), and credit card numbers. Updated regex patterns in app/pii.py to detect and mask patterns before logging. Added message_preview truncation to prevent sensitive data exposure.
- [PREVENTIVE_MEASURE]: Implemented automated PII scanning in CI/CD pipeline using validate_logs.py. Added unit tests in tests/test_pii.py to verify redaction patterns. Enabled tracing middleware to correlate PII events with specific requests/sessions. 

---

## 5. Individual Contributions & Evidence

### Nguyễn Viết Hùng
- [TASKS_COMPLETED]: Implemented PII detection and redaction patterns (email, phone, credit card). Created app/pii.py module. Developed unit tests in tests/test_pii.py. Verified 0 PII leaks in logs.jsonl dataset.
- [EVIDENCE_LINK]: [app/pii.py](app/pii.py), [tests/test_pii.py](tests/test_pii.py)

### Nguyễn Xuân Tùng
- [TASKS_COMPLETED]: Implemented distributed tracing with correlation IDs. Added request/response span creation in app/tracing.py. Enriched logs with trace context. Validated 30 complete traces captured with proper correlation.
- [EVIDENCE_LINK]: [app/tracing.py](app/tracing.py), [data/logs.jsonl](data/logs.jsonl#L1)

### Nguyễn Công Thành
- [TASKS_COMPLETED]: Defined SLO targets and error budgets in config/slo.yaml. Configured alert rules for latency, error rate, and cost thresholds. Created runbook documentation for alert response procedures.
- [EVIDENCE_LINK]: [config/slo.yaml](config/slo.yaml), [config/alert_rules.yaml](config/alert_rules.yaml)

### Trần Quốc Khánh
- [TASKS_COMPLETED]: Executed load test using scripts/load_test.py with 30 concurrent requests. Generated dashboard specification (config/logging_schema.json) with 6 panels showing latency, error rate, cost, PII events, trace distribution, and request features.
- [EVIDENCE_LINK]: [scripts/load_test.py](scripts/load_test.py), [docs/dashboard-spec.md](docs/dashboard-spec.md)

### Đỗ Đình Hoàn
- [TASKS_COMPLETED]: Coordinated team effort and prepared comprehensive lab report. Validated all components integration. Documented incident response workflow and preventive measures. Created final grading evidence summary.
- [EVIDENCE_LINK]: [docs/blueprint-template.md](docs/blueprint-template.md), [docs/grading-evidence.md](docs/grading-evidence.md) 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Implemented cost tracking per request with token counting. Tracked total cost at $0.0635 for 30 requests (avg $0.00212/req). Identified optimization opportunity: batching requests to reduce per-call overhead. Evidence: [data/logs.jsonl](data/logs.jsonl) shows cost_usd field for each response.
- [BONUS_AUDIT_LOGS]: Created comprehensive audit trail with correlation_id linking all related events. Audit log captures user_id_hash, session_id, feature type, model used, latency, and token usage. Enables complete request attribution and replay capability.
- [BONUS_CUSTOM_METRIC]: Implemented custom metric "pii_redaction_success_rate" tracking redacted patterns per session. Script: [scripts/validate_logs.py](scripts/validate_logs.py). Metric shows 100% success rate across all 30 traces with email, phone, and credit card patterns properly masked.
