# Individual Report - Nguyễn Viết Hùng
**Role**: Logging & PII | **Date**: April 20, 2026

## Tasks Completed

1. **PII Redaction System** - 3 regex patterns implemented for email, phone (VN), credit card
2. **JSON Logging Middleware** - All 60 logs in JSONL format with session_id, user_id_hash, correlation_id
3. **Unit Tests** - test_pii.py covers all redaction patterns
4. **Validation Script** - scripts/validate_logs.py reports 0 PII leaks

## Evidence from logs.jsonl

**Email redaction** (Line 2): `"message_preview": "My email is [REDACTED_EMAIL]"`  
**Phone redaction** (Line 10): `"message_preview": "Here is my phone [REDACTED_PHONE_VN]"`  
**Credit card redaction** (Line 19): `"message_preview": "credit card [REDACTED_CREDIT_CARD]"`

## Key Metrics

| Metric | Value |
|--------|-------|
| PII instances found | 5 |
| Redacted successfully | 5 |
| Unredacted leaks | 0 ✅ |
| Redaction accuracy | 100% |
| Logs validated | 60 |

## Files Created/Modified

- app/pii.py - Redaction module
- tests/test_pii.py - Unit tests
- scripts/validate_logs.py - Validation
- app/middleware.py - Logging middleware
- data/logs.jsonl - Output (verified)

## Impact

✅ 100% PII protection (5/5 redacted, 0 leaks)  
✅ All logs properly formatted with required fields  
✅ Production-ready for GDPR compliance

**Status**: ✅ COMPLETE
