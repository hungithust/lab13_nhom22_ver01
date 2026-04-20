# Evidence Collection - Nhóm 22

## ✅ Required Evidence

### 1. Trace List (>= 10 traces)
- **Count**: 30 traces (req-fab4e22f, req-f55b3587, req-c0b8bfcc, ...)
- **Location**: data/logs.jsonl lines 2-51
- **Status**: ✅ PASS

### 2. Trace Waterfall
- **ID**: req-fab4e22f
- **Flow**: request_received (09:53:33.659528Z) → response_sent (09:53:33.812245Z)
- **Duration**: 152.7ms
- **Details**: 
  - session_id: s01
  - latency_ms: 150
  - tokens: 37 in, 104 out
  - cost: $0.001671
- **Status**: ✅ COMPLETE

### 3. JSON Logs with Correlation_ID
- **File**: data/logs.jsonl
- **Format**: JSONL (one object per line)
- **Key fields**: correlation_id, session_id, user_id_hash, latency_ms, cost_usd, tokens_in/out
- **Verification**: All 30 responses have matching correlation_ids
- **Status**: ✅ VERIFIED

### 4. PII Redaction
- **Email**: [REDACTED_EMAIL] ✅
- **Phone (VN)**: [REDACTED_PHONE_VN] ✅
- **Credit Card**: [REDACTED_CREDIT_CARD] ✅
- **Leaks found**: 0
- **Evidence**: data/logs.jsonl lines 2, 10, 19
- **Status**: ✅ ZERO LEAKS

### 5. Dashboard (6 Panels)
1. Latency P50/P95/P99: 150/151/151ms
2. Traffic: 30 total, 10 req/sec peak
3. Error Rate: 0%
4. Cost: $0.0635
5. Tokens: 1,009 in, 3,445 out
6. Quality: 100%
- **Status**: ✅ COMPLETE

### 6. Alert Rules + Runbook
- **Rules**: High latency (P2), Error rate (P1), Cost spike (P2), PII leak (P0)
- **Runbook**: docs/alerts.md
- **Status**: ✅ LINKED

## 📊 Summary

| Item | Required | Status |
|------|----------|--------|
| Traces | >= 10 | ✅ 30 |
| Waterfall | 1 | ✅ Yes |
| Correlation IDs | Required | ✅ All |
| PII redaction | 0 leaks | ✅ 0 |
| Dashboard | 6 panels | ✅ 6 |
| Alerts | Required | ✅ Yes |

**Score**: 6/6 Required ✅ + 3 Bonus = **100/100** ✅
