from __future__ import annotations

import os
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

try:
    from langfuse import get_client, observe, propagate_attributes
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    def propagate_attributes(*args: Any, **kwargs: Any):
        return nullcontext()

    class _DummyContext:
        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()
else:
    class _LangfuseContext:
        def __init__(self) -> None:
            self._client = get_client()

        def update_current_observation(self, **kwargs: Any) -> None:
            metadata = dict(kwargs.get("metadata") or {})
            usage_details = kwargs.get("usage_details")
            if usage_details:
                metadata["usage_details"] = usage_details
            self._client.update_current_span(metadata=metadata or None)

    langfuse_context = _LangfuseContext()


def trace_attributes(*, user_id: str | None = None, session_id: str | None = None, tags: list[str] | None = None):
    return propagate_attributes(user_id=user_id, session_id=session_id, tags=tags)


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
