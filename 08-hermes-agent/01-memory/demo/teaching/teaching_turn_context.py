# =============================================================================
# 教学版 TurnContext / build_turn_context
# 对照源码: hermes_src/agent/turn_context.py
# =============================================================================
# 保留：prologue 主路径（sanitize → append user → system prompt →
#       preflight estimate → should_compress → compress → prefetch → return）
# 省略：MCP refresh、stdio guard、plugin spill、DB session、reaction 等旁路。
# =============================================================================
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from teaching_compressor import estimate_tokens_rough


def _compression_made_progress(
    orig_len: int, new_len: int, orig_tokens: int, new_tokens: int
) -> bool:
    """判断这一轮压缩有没有「真的变短」。

    消息条数变少，或 token 降到原来的 95% 以下 → 算有进步。
    没进步就别死循环继续压了。
    """
    if new_len < orig_len:
        return True
    return orig_tokens > 0 and new_tokens < orig_tokens * 0.95


def _should_run_preflight_estimate(
    messages: List[Dict[str, Any]],
    protect_first_n: int,
    protect_last_n: int,
    threshold_tokens: int,
) -> bool:
    """便宜门闸：值不值得做完整 token 估算。

    消息已经多到超过「头+尾保护」能盖住的范围，或者粗估已经摸到阈值 → 值得算。
    否则连估算都省掉，省一点开销。
    """
    if len(messages) > protect_first_n + protect_last_n + 1:
        return True
    return estimate_tokens_rough(messages) >= threshold_tokens


@dataclass
class TurnContext:
    """一轮对话 prologue 的产物：后面主模型 / tool loop 都吃这份。

    除了真源码字段外，多带了 compression_ran、summarizer_prompt/response，
    方便 demo 把辅助模型的入参出参打印出来。
    """

    user_message: str
    original_user_message: Any
    messages: List[Dict[str, Any]]
    conversation_history: Optional[List[Dict[str, Any]]]
    active_system_prompt: Optional[str]
    effective_task_id: str
    turn_id: str
    current_turn_user_idx: int
    should_review_memory: bool = False
    plugin_user_context: str = ""
    ext_prefetch_cache: str = ""
    # 教学扩展：压缩过程中的可观测产物（真源码不放这里）
    compression_ran: bool = False
    summarizer_prompt: str = ""
    summarizer_response: str = ""
    preflight_tokens_before: int = 0
    preflight_tokens_after: int = 0


class DemoAgent:
    """最小假 Agent：只填 build_turn_context 会摸到的字段和方法。

    真 AIAgent 有上万行；这里只模拟「缓存 system + 挂压缩机 + 调压缩」这条路径。
    """

    def __init__(
        self,
        *,
        context_compressor,
        system_prompt: str,
        memory_manager=None,
        model: str = "deepseek-chat",
        provider: str = "deepseek",
        session_id: str = "demo-session",
    ):
        """挂上压缩机、冻住的 system prompt，以及可选的 memory_manager。"""
        self.context_compressor = context_compressor
        self._cached_system_prompt = system_prompt
        self._memory_manager = memory_manager
        self.model = model
        self.provider = provider
        self.session_id = session_id
        self.platform = "demo"
        self.api_mode = "chat_completions"
        self.tools = None
        self.compression_enabled = True
        self.quiet_mode = False
        self.max_iterations = 10
        self.valid_tool_names: set[str] = set()
        self._memory_store = None
        self._memory_nudge_interval = 0
        self._turns_since_memory = 0
        self._user_turn_count = 0
        self._compression_warning = None
        self._last_compress_result = None
        self.iteration_budget = None

        # 下面这些在真源码有用；教学路径触不到，给空壳避免 AttributeError
        class _Todo:
            def has_items(self):
                return False

        class _Guard:
            def reset_for_turn(self):
                pass

        self._todo_store = _Todo()
        self._tool_guardrails = _Guard()

    def _restore_primary_runtime(self):
        """真源码会切回主 runtime；demo 不用，空实现。"""
        pass

    def _emit_status(self, msg: str):
        """真源码往控制台打状态行；demo 静默。"""
        pass

    def _safe_print(self, msg: str):
        """真源码安全打印；demo 静默（输出由 run_turn_context 的 banner/print 负责）。"""
        pass

    def _ensure_db_session(self):
        """真源码写 SQLite session；demo 跳过。"""
        pass

    def _persist_session(self, messages, conversation_history):
        """真源码落盘会话；demo 跳过。"""
        pass

    def _hydrate_todo_store(self, conversation_history):
        """真源码从历史恢复 todo；demo 跳过。"""
        pass

    def _cleanup_dead_connections(self):
        """真源码清理死连接；demo 直接说「没有要清的」。"""
        return False

    def _replay_compression_warning(self):
        """真源码重放压缩警告；demo 跳过。"""
        pass

    def _compress_context(
        self,
        messages,
        system_message,
        *,
        approx_tokens=None,
        task_id="default",
    ):
        """真正触发压缩的入口（教学版，无 DB / lock）。

        1. 问 memory_manager 要 provider_hint（别丢身份）
        2. 调 TeachingContextCompressor.compress
        3. 返回新 messages + 仍用缓存的 system prompt
        """
        self._emit_status("[pack] Compacting conversation context...")
        hint = ""
        if self._memory_manager is not None:
            try:
                hint = self._memory_manager.on_pre_compress(messages) or ""
            except Exception:
                hint = ""
        result = self.context_compressor.compress(
            messages, provider_hint=hint, force=True
        )
        self._last_compress_result = result
        # 真源码会 rebuild system prompt；教学版保持原缓存（head 已含 system 语义）
        new_system = self._cached_system_prompt
        if result.did_compress:
            # 压缩后 messages 通常不含独立 system 行；system 走 active_system_prompt
            return result.messages, new_system
        return messages, new_system


def build_turn_context(
    agent: DemoAgent,
    user_message: str,
    system_message: Optional[str],
    conversation_history: Optional[List[Dict[str, Any]]],
    task_id: Optional[str] = None,
) -> TurnContext:
    """一轮对话开始前的 prologue：拼好 messages，必要时先压缩，再交给主模型。

    主流程（对照真源码 turn_context.build_turn_context）：
      1. 给本 turn 生成 id，把用户消息 append 进 history
      2. 取出冻结的 system prompt（保 Prompt Cache）
      3. 便宜门闸 → 粗估 token → 该压就压（最多试几轮）
      4. 调 memory 的 on_turn_start / prefetch
      5. 打包成 TurnContext 返回
    """

    # --- turn ids / counters -------------------------------------------------
    effective_task_id = task_id or str(uuid.uuid4())
    agent._current_task_id = effective_task_id
    turn_id = f"{agent.session_id}:{effective_task_id}:{uuid.uuid4().hex[:8]}"
    agent._current_turn_id = turn_id
    agent._user_turn_count += 1

    messages = list(conversation_history) if conversation_history else []
    original_user_message = user_message

    # --- append this turn's user message ------------------------------------
    messages.append({"role": "user", "content": user_message})
    current_turn_user_idx = len(messages) - 1
    agent._safe_print(
        f"[chat] Starting conversation: '{user_message[:60]}"
        f"{'...' if len(user_message) > 60 else ''}'"
    )

    # --- system prompt (cached) ---------------------------------------------
    if agent._cached_system_prompt is None and system_message:
        agent._cached_system_prompt = system_message
    active_system_prompt = agent._cached_system_prompt

    # --- preflight compression ----------------------------------------------
    compression_ran = False
    summarizer_prompt = ""
    summarizer_response = ""
    preflight_before = 0
    preflight_after = 0

    compressor = agent.context_compressor
    if agent.compression_enabled and _should_run_preflight_estimate(
        messages,
        compressor.protect_first_n,
        compressor.protect_last_n,
        compressor.threshold_tokens,
    ):
        preflight_before = estimate_tokens_rough(messages) + len(
            active_system_prompt or ""
        ) // 4
        if compressor.last_prompt_tokens >= 0 and preflight_before > compressor.last_prompt_tokens:
            compressor.last_prompt_tokens = preflight_before

        if compressor.should_compress(preflight_before):
            agent._emit_status(
                f"[pack] Preflight compression: ~{preflight_before:,} tokens "
                f">= {compressor.threshold_tokens:,} threshold."
            )
            for _pass in range(3):
                orig_len = len(messages)
                orig_tokens = preflight_before
                messages, active_system_prompt = agent._compress_context(
                    messages,
                    system_message,
                    approx_tokens=preflight_before,
                    task_id=effective_task_id,
                )
                result = agent._last_compress_result
                if result and result.did_compress:
                    compression_ran = True
                    summarizer_prompt = result.summarizer_prompt
                    summarizer_response = result.summary
                preflight_before = estimate_tokens_rough(messages) + len(
                    active_system_prompt or ""
                ) // 4
                if not _compression_made_progress(
                    orig_len, len(messages), orig_tokens, preflight_before
                ):
                    break
                conversation_history = list(messages)
                if not compressor.should_compress(preflight_before):
                    break
            preflight_after = preflight_before
        else:
            preflight_after = preflight_before

    # --- memory provider hooks ----------------------------------------------
    ext_prefetch_cache = ""
    if agent._memory_manager:
        try:
            agent._memory_manager.on_turn_start(
                agent._user_turn_count, original_user_message
            )
        except Exception:
            pass
        try:
            ext_prefetch_cache = (
                agent._memory_manager.prefetch_all(original_user_message) or ""
            )
        except Exception:
            pass

    return TurnContext(
        user_message=user_message,
        original_user_message=original_user_message,
        messages=messages,
        conversation_history=conversation_history,
        active_system_prompt=active_system_prompt,
        effective_task_id=effective_task_id,
        turn_id=turn_id,
        current_turn_user_idx=current_turn_user_idx,
        should_review_memory=False,
        plugin_user_context="",
        ext_prefetch_cache=ext_prefetch_cache,
        compression_ran=compression_ran,
        summarizer_prompt=summarizer_prompt,
        summarizer_response=summarizer_response,
        preflight_tokens_before=preflight_before if compression_ran else preflight_before,
        preflight_tokens_after=preflight_after,
    )
