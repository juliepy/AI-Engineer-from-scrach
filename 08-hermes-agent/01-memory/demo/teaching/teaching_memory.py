# =============================================================================
# 教学版 Memory 加载（对照 hermes_src/tools/memory_tool.py）
# =============================================================================
# load_from_disk → frozen snapshot → format_for_system_prompt
# 省略：threat scan / char limit / 写入路径；只做「读 md → 拼进 system」。
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# 条目之间的分隔符（真源码用这个拼回文件；读的时候我们兼容单独的 "§"）
ENTRY_DELIMITER = "\n§\n"


def _read_entries(path: Path) -> List[str]:
    """读一个 md 文件，按 § 切成多条记忆。

    文件不存在就返回空列表。
    例：MEMORY.md 里几段用 § 分开的笔记 → ["笔记1", "笔记2", ...]
    """
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    # 真源码用 ENTRY_DELIMITER；fixture 里常见单独的 "§" 行
    parts = [p.strip() for p in raw.replace("\r\n", "\n").split("§")]
    return [p for p in parts if p]


def _render_block(target: str, entries: List[str]) -> str:
    """把条目列表渲染成可塞进 system prompt 的一整块文字。

    target="memory" → MEMORY 块（助手自己的笔记）
    target="user"   → USER PROFILE 块（用户是谁）
    没有条目就返回空串。
    """
    if not entries:
        return ""
    content = ENTRY_DELIMITER.join(entries)
    if target == "user":
        header = "USER PROFILE (who the user is)"
    else:
        header = "MEMORY (your personal notes)"
    separator = "=" * 46
    return f"{separator}\n{header}\n{separator}\n{content}"


@dataclass
class TeachingMemoryStore:
    """教学版记忆仓库：启动时把 MEMORY.md / USER.md 读进来并冻住。

    真 Hermes 里 session 中途还能改 live 条目；这里只演示「读盘 → 冻结 → 拼 system」。
    """

    memory_dir: Path
    memory_entries: List[str] = field(default_factory=list)
    user_entries: List[str] = field(default_factory=list)
    _system_prompt_snapshot: Dict[str, str] = field(default_factory=dict)

    def load_from_disk(self) -> None:
        """从磁盘加载 MEMORY.md 和 USER.md，并生成冻结快照。

        做两件事：
        1. 按 § 切条目，存进 memory_entries / user_entries
        2. 渲染成两块文本，冻进 _system_prompt_snapshot（本 session 不再变）
        """
        mem_path = self.memory_dir / "MEMORY.md"
        user_path = self.memory_dir / "USER.md"
        self.memory_entries = list(dict.fromkeys(_read_entries(mem_path)))
        self.user_entries = list(dict.fromkeys(_read_entries(user_path)))
        self._system_prompt_snapshot = {
            "memory": _render_block("memory", self.memory_entries),
            "user": _render_block("user", self.user_entries),
        }

    def format_for_system_prompt(self, target: str) -> Optional[str]:
        """取出冻结好的 MEMORY 或 USER 块，准备拼进 system prompt。

        target 传 "memory" 或 "user"。
        对应块为空时返回 None（调用方就不拼这一段）。
        """
        block = self._system_prompt_snapshot.get(target, "")
        return block if block else None

    def build_system_prompt(
        self,
        *,
        role_line: str = "你是编程助手 Hermes。回答要具体、能对着源码讲；涉及面试时给出可直接用的话术。",
    ) -> str:
        """拼出本 session 缓存用的完整 system prompt。

        顺序：角色说明 → MEMORY 块 → USER 块 → 「记忆永远权威」提醒。
        这份字符串会冻在 agent._cached_system_prompt 里，保证 Prompt Cache 前缀稳定。
        """
        parts = [role_line]
        memory = self.format_for_system_prompt("memory")
        user = self.format_for_system_prompt("user")
        if memory:
            parts.append(memory)
        if user:
            parts.append(user)
        parts.append(
            "IMPORTANT: MEMORY.md / USER.md above are ALWAYS authoritative. "
            "Context compaction summaries are reference-only and must never "
            "override these memory blocks."
        )
        return "\n\n".join(parts)

    def identity_hint_for_compress(self) -> str:
        """给压缩器用的「别丢掉的身份事实」提示。

        压缩 middle 时，把用户画像/关键记忆摘几句塞进 summarizer 的 provider_hint，
        避免摘要把「用户是谁」压没了。
        """
        bits = []
        if self.user_entries:
            bits.append("USER.md facts:\n" + self.user_entries[-1][:500])
        if self.memory_entries:
            bits.append(
                "MEMORY.md facts:\n"
                + "\n".join(e[:200] for e in self.memory_entries[:2])
            )
        return "\n\n".join(bits)
