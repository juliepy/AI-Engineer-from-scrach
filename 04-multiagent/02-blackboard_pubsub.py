# =============================================================================
#  3.4 黑板 + Pub-Sub + 简单消息队列（内存版教学）
# =============================================================================
#
#  多 Agent 协作常见三种通信模式（生产环境应换 Redis / RabbitMQ / Kafka 等）：
#
#  1. 黑板（Blackboard）：共享状态区，各 Agent 读写同一份结构化数据
#  2. 发布订阅（Pub-Sub）：事件驱动，完成某步后广播，订阅者异步响应
#  3. 消息队列（Queue）：生产者入队、消费者出队，解耦与削峰
#
#  ── 代码设计图 ────────────────────────────────────────────────────────────────
#
#  【黑板】
#    Agent A ──write("plan", ...)──► Blackboard ──read("plan")──► Agent B
#
#  【Pub-Sub】
#    Agent C ──publish("task.done", payload)──► PubSub ──► handler₁, handler₂
#
#  【消息队列】
#    Producer ──enqueue(item)──► InMemoryQueue ──dequeue()──► Consumer
#
# =============================================================================

import sys
import threading
from collections import defaultdict, deque
from typing import Any, Callable, Deque, DefaultDict, Dict, List, Optional

sys.stdout.reconfigure(encoding="utf-8")


class Blackboard:
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def write(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value

    def read(self, key: str) -> Any:
        with self._lock:
            return self._data.get(key)


class PubSub:
    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[Callable[[str, Any], None]]] = (
            defaultdict(list)
        )

    def subscribe(self, topic: str, handler: Callable[[str, Any], None]) -> None:
        self._subs[topic].append(handler)

    def publish(self, topic: str, payload: Any) -> None:
        for h in self._subs.get(topic, []):
            h(topic, payload)


class InMemoryQueue:
    """简单消息队列（内存版，教学用）。"""

    def __init__(self) -> None:
        self._q: Deque[Any] = deque()
        self._lock = threading.Lock()

    def enqueue(self, item: Any) -> None:
        with self._lock:
            self._q.append(item)

    def dequeue(self) -> Optional[Any]:
        with self._lock:
            if not self._q:
                return None
            return self._q.popleft()

    def size(self) -> int:
        with self._lock:
            return len(self._q)


if __name__ == "__main__":
    print("=== 黑板 Blackboard ===")
    bb = Blackboard()
    bb.write("plan", {"steps": ["analyze", "code", "test"]})
    bb.write("status", "analyst_done")
    print("plan  =", bb.read("plan"))
    print("status=", bb.read("status"))
    print()

    print("=== Pub-Sub ===")
    bus = PubSub()

    def on_task_done(topic: str, payload: Any) -> None:
        print(f"  [handler] {topic} → {payload}")

    def on_task_done_audit(topic: str, payload: Any) -> None:
        print(f"  [audit]   agent={payload.get('agent')} ok={payload.get('ok')}")

    bus.subscribe("task.done", on_task_done)
    bus.subscribe("task.done", on_task_done_audit)
    bus.publish("task.done", {"agent": "coder", "ok": True})
    print()

    print("=== 消息队列 InMemoryQueue ===")
    q = InMemoryQueue()
    q.enqueue({"task": "analyze", "priority": 1})
    q.enqueue({"task": "code", "priority": 2})
    print("队列长度:", q.size())
    while q.size():
        item = q.dequeue()
        print("  出队:", item)
