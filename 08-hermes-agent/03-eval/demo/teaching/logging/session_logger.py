"""教学版 session_tag 日志（对照 hermes_logging.py 核心机制）。

真源码：set_session_context + LogRecord factory 注入 %(session_tag)s；
COMPONENT_PREFIXES 分流 gateway/agent/tools。

本文件不依赖 concurrent-log-handler / get_hermes_home，只演示可观测性契约。
"""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from io import StringIO

_session_context = threading.local()

_LOG_FORMAT = "%(asctime)s %(levelname)s%(session_tag)s %(name)s: %(message)s"

COMPONENT_PREFIXES = {
    "gateway": ("gateway", "hermes_plugins", "plugins.platforms"),
    "agent": ("agent", "run_agent", "model_tools", "batch_runner"),
    "tools": ("tools",),
    "cli": ("hermes_cli", "cli"),
}


def set_session_context(session_id: str) -> None:
    _session_context.session_id = session_id


def clear_session_context() -> None:
    _session_context.session_id = None


def _install_session_record_factory() -> None:
    current = logging.getLogRecordFactory()
    if getattr(current, "_teaching_session_injector", False):
        return

    def factory(*args, **kwargs):
        record = current(*args, **kwargs)
        sid = getattr(_session_context, "session_id", None)
        record.session_tag = f" [{sid}]" if sid else ""  # type: ignore[attr-defined]
        return record

    factory._teaching_session_injector = True  # type: ignore[attr-defined]
    logging.setLogRecordFactory(factory)


_install_session_record_factory()


class ComponentFilter(logging.Filter):
    def __init__(self, prefixes: tuple[str, ...]):
        super().__init__()
        self.prefixes = prefixes

    def filter(self, record: logging.LogRecord) -> bool:
        name = record.name
        return any(name == p or name.startswith(p + ".") for p in self.prefixes)


@dataclass
class CapturedLogs:
    """内存里的 agent.log / errors.log 切片，便于导出。"""

    agent: StringIO = field(default_factory=StringIO)
    errors: StringIO = field(default_factory=StringIO)
    by_component: dict[str, StringIO] = field(default_factory=dict)

    def agent_text(self) -> str:
        return self.agent.getvalue()

    def errors_text(self) -> str:
        return self.errors.getvalue()

    def component_text(self, component: str) -> str:
        buf = self.by_component.get(component)
        return buf.getvalue() if buf else ""


def setup_teaching_logging() -> CapturedLogs:
    """把 root logger 接到内存 handler，模拟 agent.log / errors.log / component 切片。"""
    captured = CapturedLogs()
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(_LOG_FORMAT)

    agent_h = logging.StreamHandler(captured.agent)
    agent_h.setLevel(logging.INFO)
    agent_h.setFormatter(fmt)
    root.addHandler(agent_h)

    err_h = logging.StreamHandler(captured.errors)
    err_h.setLevel(logging.WARNING)
    err_h.setFormatter(fmt)
    root.addHandler(err_h)

    for comp, prefixes in COMPONENT_PREFIXES.items():
        buf = StringIO()
        captured.by_component[comp] = buf
        h = logging.StreamHandler(buf)
        h.setLevel(logging.INFO)
        h.setFormatter(fmt)
        h.addFilter(ComponentFilter(prefixes))
        root.addHandler(h)

    return captured


def demo_emit_session_logs(session_id: str = "sess_eval_demo") -> CapturedLogs:
    """模拟一轮对话产生的跨组件日志（含 session_tag）。"""
    captured = setup_teaching_logging()
    set_session_context(session_id)
    try:
        logging.getLogger("agent.conversation_loop").info("API call #1: model=deepseek cache=hit")
        logging.getLogger("tools.web_search").info("web_search query=%s", "conversation_loop")
        logging.getLogger("gateway.platforms.telegram").info("delivery ok chat=123")
        logging.getLogger("agent.conversation_loop").warning("budget remaining=0 → grace call")
        logging.getLogger("tools.registry").error("dispatch failed: tool not found")
    finally:
        clear_session_context()
    # 无 session 的行（对照：tag 为空）
    logging.getLogger("hermes_cli.main").info("cli idle")
    return captured


def filter_log_by_session(log_text: str, session_id: str) -> list[str]:
    needle = f"[{session_id}]"
    return [ln for ln in log_text.splitlines() if needle in ln]
