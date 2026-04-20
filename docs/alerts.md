# Alert Runbooks — Day 13 Observability Lab

---

## 1. High latency P95

**Alert:** `latency_p95_ms > 5000 for 30m` | **Severity:** P2

### Xác nhận
```bash
curl http://localhost:8000/metrics | jq '{p50:.latency_p50, p95:.latency_p95, p99:.latency_p99}'
curl http://localhost:8000/health  | jq '.incidents'
```
Nếu `p95 > 5000` → confirmed. Nếu chỉ `p99` cao nhưng `p95` ổn → theo dõi thêm, chưa P2.

### Khu trú — dùng Trace Waterfall trên Langfuse
Langfuse → filter traces `duration > 3000ms` → xem từng span:
```
├── retrieve()      [?? ms]  ← nếu ~2500ms → rag_slow incident đang bật
└── llm.generate()  [?? ms]  ← nếu > 1000ms → model latency (không phải incident)
```

```bash
# Tìm request chậm từ logs
jq 'select(.latency_ms != null and .latency_ms > 3000)
    | {ts, correlation_id, latency_ms, feature}' data/logs.jsonl
```

### Giải quyết
```bash
python scripts/inject_incident.py --scenario rag_slow --disable
curl http://localhost:8000/metrics | jq '.latency_p95'   # verify đã về bình thường
```

### Phòng ngừa
- Thêm timeout cho RAG call (mock_rag.py hiện không có timeout)
- Cache kết quả retrieve cho query lặp lại
- Fallback retrieval source khi primary chậm

---

## 2. High error rate

**Alert:** `error_rate_pct > 5 for 5m` | **Severity:** P1

### Xác nhận
```bash
curl http://localhost:8000/metrics | jq '{traffic:.traffic, errors:.error_breakdown}'
# error_rate = tổng errors / traffic × 100
# traffic=10, RuntimeError=5 → error_rate=50% → confirmed P1
```

### Khu trú
```bash
# Phân loại lỗi từ logs
jq 'select(.event == "request_failed") | .error_type' data/logs.jsonl | sort | uniq -c

# Chi tiết 1 lỗi
jq 'select(.event == "request_failed") | {ts, correlation_id, error_type, payload}' data/logs.jsonl | head -3
```

| error_type | Nguyên nhân | Incident |
|---|---|---|
| `RuntimeError` | Vector store timeout | `tool_fail` |
| `ValidationError` | Request schema sai | Code bug |

```bash
# Xác nhận tool_fail
curl http://localhost:8000/health | jq '.incidents.tool_fail'   # true = đang bật
```

### Giải quyết
```bash
python scripts/inject_incident.py --scenario tool_fail --disable
curl http://localhost:8000/metrics | jq '.error_breakdown'   # verify về {}
```

### Phòng ngừa
- Retry logic với exponential backoff trong mock_rag.py
- Circuit breaker: tool fail 3 lần → trả fallback answer thay vì raise exception
- Alert riêng cho từng error_type để phân loại nhanh hơn

---

## 3. Cost budget spike

**Alert:** `hourly_cost_usd > 2x_baseline for 15m` | **Severity:** P2

### Xác nhận
```bash
curl http://localhost:8000/metrics | jq '{
  total_cost: .total_cost_usd,
  avg_cost:   .avg_cost_usd,
  tokens_out: .tokens_out_total
}'
# Cost bình thường (10 req): ~$0.023
# Cost khi cost_spike (tokens_out×4): ~$0.081 → tăng ~3.5×
```

### Khu trú
```bash
# Request nào tốn nhiều token nhất?
jq 'select(.tokens_out != null)
    | {ts, feature, tokens_in, tokens_out, cost_usd}' data/logs.jsonl \
  | jq -s 'sort_by(.tokens_out) | reverse | .[0:3]'

# Kiểm tra incident
curl http://localhost:8000/health | jq '.incidents.cost_spike'
```
Trong Langfuse: sort traces by `usage.output` descending → xem feature tag nào tốn nhất.

### Giải quyết
```bash
python scripts/inject_incident.py --scenario cost_spike --disable
curl http://localhost:8000/metrics | jq '.avg_cost_usd'   # verify về bình thường
```

### Phòng ngừa
- Giới hạn `max_tokens` trong FakeLLM.generate() (hiện không có cap)
- Route câu hỏi ngắn sang model rẻ hơn (claude-haiku)
- Thêm cost per request vào response log để monitor realtime

---

## 4. Low quality score

**Alert:** `quality_score_avg < 0.6 for 20m` | **Severity:** P3

### Xác nhận
```bash
curl http://localhost:8000/metrics | jq '.quality_avg'
# < 0.6 → confirmed
```

### Khu trú — hiểu score breakdown
`_heuristic_quality()` trong `agent.py`:
```
base          = 0.5   (luôn có)
+ 0.2  nếu docs != []          ← RAG có trả về kết quả không?
+ 0.1  nếu len(answer) > 40    ← Answer đủ dài không?
+ 0.1  nếu keyword match       ← Answer liên quan đến câu hỏi không?
- 0.2  nếu "[REDACTED" trong answer  ← PII scrub làm hỏng answer?
```

```bash
# Quality từng request
jq 'select(.quality_score != null)
    | {ts, feature, quality_score}' data/logs.jsonl

# Test query có khớp corpus không
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"user_id":"u1","session_id":"s1","message":"refund policy"}'
# → "refund" khớp CORPUS → doc_count=1 → score ~0.90

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"user_id":"u1","session_id":"s1","message":"random xyz question"}'
# → không khớp → fallback answer → score ~0.70
```

Trong Langfuse: xem `doc_count` trong trace metadata — nếu = 0 liên tục → corpus miss.

### Giải quyết
- Mở rộng CORPUS trong mock_rag.py với thêm keywords
- Kiểm tra PII scrubbing có đang xóa nội dung hợp lệ không

### Phòng ngừa
- Thêm BM25 / fuzzy matching thay vì exact keyword match trong mock_rag.py
- User feedback (thumbs up/down) để calibrate heuristic scoring

---

## 5. No traffic — Dead man's switch

**Alert:** `request_count == 0 for 10m` | **Severity:** P1

### Xác nhận
```bash
curl http://localhost:8000/health   # Connection refused = app chết; {"ok":true} = app sống nhưng không có traffic
ps aux | grep uvicorn               # kiểm tra process
lsof -i :8000                       # kiểm tra port có bind không
```

### Khu trú

**Case 1: App đã crash**
```bash
tail -20 data/logs.jsonl | jq '{ts, event, level}'   # log cuối trước khi crash
# Restart:
uvicorn app.main:app --reload
```

**Case 2: App sống, không nhận traffic**
- Kiểm tra load balancer / reverse proxy config
- Kiểm tra firewall rules trên port 8000

**Case 3: Môi trường dev, chưa chạy load test**
```bash
python scripts/load_test.py
curl http://localhost:8000/metrics | jq '.traffic'   # verify > 0
```

### Phòng ngừa
- Process supervisor (systemd, supervisor) để auto-restart khi crash
- Synthetic monitoring: ping `/health` mỗi 30 giây từ external monitor
- Readiness probe riêng biệt với liveness probe trong Kubernetes