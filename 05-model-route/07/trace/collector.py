import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .kinds import SpanKind


@dataclass
class Span:
    trace_id: str
    span_id: str
    kind: SpanKind
    name: str
    start_ms: float
    end_ms: float
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Trace:
    trace_id: str
    goal: str
    spans: List[Span] = field(default_factory=list)

    def start_span(
        self,
        kind: SpanKind,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> "SpanBuilder":
        return SpanBuilder(self, kind, name, attributes or {})


class SpanBuilder:
    def __init__(self, trace: Trace, kind: SpanKind, name: str, attrs: Dict[str, Any]):
        self.trace = trace
        self.kind = kind
        self.name = name
        self.attrs = dict(attrs)
        self.t0 = time.perf_counter()

    def set_attr(self, key: str, value: Any) -> "SpanBuilder":
        self.attrs[key] = value
        return self

    def end(self) -> Span:
        span = Span(
            trace_id=self.trace.trace_id,
            span_id=uuid.uuid4().hex[:8],
            kind=self.kind,
            name=self.name,
            start_ms=self.t0 * 1000,
            end_ms=time.perf_counter() * 1000,
            attributes=self.attrs,
        )
        self.trace.spans.append(span)
        return span
