# Individual Report - Nguyễn Xuân Tùng
**Role**: Tracing & Enrichment | **Date**: April 20, 2026

## Tasks Completed

1. **Correlation IDs** - 30 unique traces (req-fab4e22f, req-f55b3587, etc.)
2. **Span Tracking** - request_received → response_sent events for all traces
3. **Enrichment Fields** - session_id, user_id_hash, feature, model added to all logs
4. **Metrics Collection** - latency_ms, tokens_in/out, cost_usd tracked per request

## Evidence from logs.jsonl (Lines 2-3)

**req-fab4e22f trace**:  
Request: `ts: 2026-04-20T09:53:33.659528Z, session_id: s01, user_id_hash: 2055254ee30a`  
Response: `latency_ms: 150, tokens_in: 37, tokens_out: 104, cost_usd: 0.001671`

## Key Metrics

| Metric | Value |
|--------|-------|
| Total traces | 30 |
| Correlation ID coverage | 100% |
| Avg latency | 150.1ms |
| Latency range | 150-151ms |
| Consistency | 99.8% |
| Features tracked | qa (20), summary (10) |
| Sessions | 10 unique |
| Users | 15 unique |

## Files Created/Modified

- app/tracing.py - Trace generation
- app/middleware.py - Enrichment logic
- config/logging_schema.json - Schema
- data/logs.jsonl - Output traces

## Impact

✅ 100% request tracing with correlation IDs  
✅ Full request-response visibility  
✅ Cost attribution enabled  
✅ Session/user journey tracking

**Status**: ✅ COMPLETE - 30 traces, 100% coverage
