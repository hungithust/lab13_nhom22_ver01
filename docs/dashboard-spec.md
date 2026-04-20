# Dashboard Spec - Nhóm 22

## Implemented Panels (6 Total)

1. **Latency P50/P95/P99**: 150ms / 151ms / 151ms
   - SLO target: < 3000ms ✅
   - Source: latency_ms field in response_sent events

2. **Traffic (QPS)**
   - Total: 30 requests over ~2 minutes
   - Peak: 10 req/sec
   - By feature: qa (20), summary (10)

3. **Error Rate**
   - Current: 0% (30/30 successful)
   - SLO target: < 2% ✅

4. **Cost Over Time**
   - Total: $0.0635 (30 requests)
   - Avg per request: $0.00212
   - SLO budget: $2.50/day ✅
   - Model: claude-sonnet-4-5 (100%)

5. **Tokens In/Out**
   - Total in: 1,009 (avg 33.6/request)
   - Total out: 3,445 (avg 114.8/request)
   - Ratio: 1:3.4 (output-heavy)

6. **Quality Proxy**
   - Success rate: 100% (all first-attempt)
   - Quality score: 100/100

## Configuration

| Setting | Value |
|---------|-------|
| Time range | 1 hour default |
| Refresh | 20 seconds |
| Panels | 6 (2x3 grid) |
| Units | ms, %, req/sec, USD, tokens |
| Color scheme | Green ✅ / Yellow ⚠ / Red ❌ |

## Data Source

- Logs: `data/logs.jsonl`
- Schema: `config/logging_schema.json`
- Metrics engine: `app/metrics.py`

**Status**: ✅ All SLOs healthy
