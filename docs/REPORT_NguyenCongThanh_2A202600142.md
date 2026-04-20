# Individual Report - Nguyễn Công Thành
**Role**: SLO & Alerts | **Date**: April 20, 2026

## Tasks Completed

1. **SLO Definition** - 4 SLOs defined: Latency P95, Error Rate, Cost/day, PII Leaks
2. **Alert Rules** - 4 alerts configured in config/alert_rules.yaml
3. **Runbooks** - 4 incident runbooks created in docs/alerts.md
4. **Error Budget** - 2% monthly budget with 100% remaining

## Current Performance vs Targets

| SLI | Target | Current | Status |
|-----|--------|---------|--------|
| Latency P95 | < 3000ms | 151ms | ✅ |
| Error Rate | < 2% | 0% | ✅ |
| Cost/day | < $2.50 | $0.0635 | ✅ |
| PII Leaks | 0 | 0 | ✅ |

## Alert Rules

1. **high_latency_p95** - P2, trigger > 3000ms for 5min
2. **high_error_rate** - P1, trigger > 2% for 5min  
3. **cost_budget_spike** - P2, trigger > $2.50/day
4. **pii_leak** - P0, trigger > 0 unredacted PII

## Evidence from logs.jsonl

- Latency: 30 responses, all 150-151ms (vs target 3000ms)
- Errors: 30/30 success, 0% error rate (vs target 2%)
- Cost: $0.0635 total (vs budget $2.50)
- PII: 0 leaks found (verified by scripts/validate_logs.py)

## Files Created/Modified

- config/slo.yaml - SLO targets
- config/alert_rules.yaml - Alert configuration
- docs/alerts.md - 4 incident runbooks

## Impact

✅ All 4 SLOs healthy  
✅ 4 alerts armed for incident detection  
✅ Runbooks enable fast MTTR  
✅ 100% error budget remaining

**Status**: ✅ COMPLETE - SLOs met, alerts ready
