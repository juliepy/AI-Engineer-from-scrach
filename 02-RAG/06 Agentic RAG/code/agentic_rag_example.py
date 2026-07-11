#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现场练习示例 · ISA 从 Naive RAG 升级为 Agentic RAG
====================================================
覆盖练习四项:
  ① 给 Agent 加工具:search_docs / search_web / calculator
  ② 写 Agent 路由 System Prompt(多向量库)
  ③ 跑对比:Naive vs Agentic
  ④ 接入 LangSmith,产出完整 Trace

运行:
  pip install openai langsmith python-dotenv
  # 在项目根目录 .env 中配置 DEEPSEEK_API_KEY=sk-...
  # 可选:开启 LangSmith 追踪(练习④)
  export LANGSMITH_TRACING=true
  export LANGSMITH_API_KEY=ls-...
  export LANGSMITH_PROJECT=isa-agentic-rag
  python3 agentic_rag_example.py

说明:向量库/网页搜索用「教学级 mock」实现,不用真的向量数据库也能跑通、看清决策链路。
      DeepSeek 兼容 OpenAI tool calling,结构不变。
"""

import os
import re
import json
import time

from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("请在 .env 中配置 DEEPSEEK_API_KEY")

# ---- LangSmith 追踪(练习④)。没装/没配也能跑,traceable 会退化为普通函数 ----
try:
    from langsmith import traceable
    from langsmith.wrappers import wrap_openai
    client = wrap_openai(OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    ))          # 自动把每次 LLM 调用记进 Trace
except Exception:
    def traceable(*a, **k):                  # 优雅降级:没有 langsmith 时的空装饰器
        def deco(fn): return fn
        return deco if not (a and callable(a[0])) else a[0]
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )

MODEL = "deepseek-chat"

# ============================================================
# ① 工具:三个向量库(多库路由)+ 网页搜索 + 计算器
# ============================================================
# 三个「向量库」——按知识域分库,模拟生产里的多 index(练习里的多库路由重头戏)
VECTOR_STORES = {
    "product": {   # 产品文档
        "ISA 支持三种检索模式:关键词、向量、混合检索。": 0.0,
        "ISA 的向量库默认返回 top-5,可通过 top_k 参数调整。": 0.0,
    },
    "policy": {    # 政策 / 合规
        "退款政策:购买后 14 天内可全额退款,需提供订单号。": 0.0,
        "数据合规:用户 PII 必须脱敏后才能写入日志。": 0.0,
    },
    "tickets": {   # 历史工单
        "工单 #1024:客户反馈检索慢,已通过增加 top_k 缓存解决。": 0.0,
    },
}


def _keyword_score(query: str, text: str) -> float:
    """极简相关性打分(教学用),真实中换成向量相似度。"""
    q = set(re.findall(r"[\w一-鿿]+", query.lower()))
    t = set(re.findall(r"[\w一-鿿]+", text.lower()))
    return len(q & t) / (len(q) + 1e-9)


@traceable(name="search_docs", run_type="retriever")
def search_docs(query: str, store: str = "product", top_k: int = 3) -> str:
    """向量搜索内部文档。store ∈ {product, policy, tickets};可多次调用搜不同库。"""
    docs = VECTOR_STORES.get(store, {})
    scored = sorted(
        ({"text": t, "score": round(_keyword_score(query, t), 3)} for t in docs),
        key=lambda d: d["score"], reverse=True,
    )[:top_k]
    scored = [d for d in scored if d["score"] > 0]      # 过滤完全不相关的
    if not scored:
        return json.dumps({"status": "empty", "store": store, "results": []}, ensure_ascii=False)
    return json.dumps({"status": "ok", "store": store, "results": scored}, ensure_ascii=False)


@traceable(name="search_web", run_type="tool")
def search_web(query: str) -> str:
    """网页搜索——内部文档不够时补充。教学用 mock。"""
    time.sleep(0.2)
    return json.dumps(
        {"status": "ok", "results": [f"[web] 关于「{query}」的公开资料摘要 …"]},
        ensure_ascii=False,
    )


@traceable(name="calculator", run_type="tool")
def calculator(expr: str) -> str:
    """数值计算。⚠️ 生产禁用裸 eval,这里用受限白名单解析。"""
    if not re.fullmatch(r"[\d\.\+\-\*\/\(\)\s]+", expr or ""):
        return json.dumps({"status": "error", "msg": "非法表达式"}, ensure_ascii=False)
    try:
        return json.dumps({"status": "ok", "result": eval(expr, {"__builtins__": {}})}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "msg": str(e)}, ensure_ascii=False)


# OpenAI tool schema —— 告诉模型每个工具的名字/用途/参数
TOOLS_SCHEMA = [
    {"type": "function", "function": {
        "name": "search_docs", "description": "向量搜索内部文档。store 可选 product(产品) / policy(政策合规) / tickets(历史工单),需要时可多次调用搜不同库。",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"},
            "store": {"type": "string", "enum": ["product", "policy", "tickets"]},
            "top_k": {"type": "integer"}}, "required": ["query", "store"]}}},
    {"type": "function", "function": {
        "name": "search_web", "description": "网页搜索,当内部文档不足时补充外部信息。",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "calculator", "description": "数值计算,如百分比、汇总。",
        "parameters": {"type": "object", "properties": {"expr": {"type": "string"}}, "required": ["expr"]}}},
]
TOOL_FUNCS = {"search_docs": search_docs, "search_web": search_web, "calculator": calculator}


# ============================================================
# ② Agent 路由 System Prompt(多库版)
# ============================================================
SYSTEM_PROMPT = """你是 ISA 知识助手。根据用户问题选择合适策略:

1. 可以直接回答(如"你好""谢谢")→ 直接回答,不调用任何工具
2. 需要查内部知识 → 调用 search_docs,并选对向量库:
   - product : 产品功能、用法、参数
   - policy  : 退款、合规、数据政策
   - tickets : 历史工单、故障处理经验
   跨域问题可分别搜多个库。
3. 内部文档不够 → 补充调用 search_web
4. 需要计算 → 调用 calculator
5. 检索结果为空或不相关 → 可改写 query 再搜(最多重试 2 次)
6. 仍找不到 → 明确回答:"文档中没有足够信息回答这个问题"

重要:不要编造信息,回答必须基于检索到的内容,并说明来源库。"""


# ============================================================
# LLM 调用(被 LangSmith 自动追踪)
# ============================================================
def call_llm(messages, use_tools=True):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS_SCHEMA if use_tools else None,
        temperature=0,
    )


# ============================================================
# Agentic RAG 主循环(含错误恢复 + 降级)
# ============================================================
@traceable(name="agentic_rag", run_type="chain")
def agentic_rag(question: str, max_steps: int = 5) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for step in range(max_steps):                     # 停止条件:最多 5 轮决策
        try:
            resp = call_llm(messages).choices[0].message
        except Exception as e:
            # 降级:LLM 服务异常 → 兜底回答
            return f"[降级] 服务暂时不可用({e}),请稍后重试。"

        if not resp.tool_calls:
            return resp.content                       # Agent 决定直接回答

        # Agent 决定调工具 —— 逐个执行并回填
        messages.append(resp)
        for call in resp.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            print(f"  🔧 第{step+1}轮 调用 {name}({args})")
            try:
                result = TOOL_FUNCS[name](**args)     # 执行工具
            except Exception as e:
                result = json.dumps({"status": "error", "msg": str(e)}, ensure_ascii=False)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    # 触发步数上限 → 降级拒答
    return "无法在有限步数内可靠回答,建议换个问法或缩小问题范围。"


# ============================================================
# Naive RAG 基线(用于对比)—— 无脑固定流程
# ============================================================
@traceable(name="naive_rag", run_type="chain")
def naive_rag(question: str) -> str:
    # 每次都检索、固定搜 product 库、固定 top-5、一次生成
    ctx = search_docs(question, store="product", top_k=5)
    messages = [
        {"role": "system", "content": "根据以下检索内容回答问题,无关就照实说。"},
        {"role": "user", "content": f"检索内容:{ctx}\n\n问题:{question}"},
    ]
    return call_llm(messages, use_tools=False).choices[0].message.content


# ============================================================
# ③ 对比跑分:Naive vs Agentic(练习要求测 10 个问题)
# ============================================================
TEST_QUESTIONS = [
    "你好",                                   # 不该检索:Agentic 更快
    "ISA 支持哪几种检索模式?",                 # product 库
    "退款政策是怎样的?",                       # policy 库(Naive 固定搜 product 会漏)
    "以前有没有处理过检索慢的工单?",           # tickets 库
    "对比 ISA 的向量检索和网页搜索各自适合什么", # 跨域 / 可能需多次检索
    "top-5 检索,如果每条文档 200 token,总共多少 token?",  # 需要 calculator
]


def main():
    print("=" * 64)
    print("  ISA 现场练习 · Naive RAG  vs  Agentic RAG")
    if os.getenv("LANGSMITH_TRACING") == "true":
        print("  ✅ LangSmith 追踪已开启,去 dashboard 看完整 Trace")
    print("=" * 64)

    for q in TEST_QUESTIONS:
        print(f"\n❓ 问题:{q}")
        t0 = time.time()
        a = agentic_rag(q)
        dt_a = time.time() - t0
        print(f"🧠 Agentic({dt_a:.1f}s):{a}\n")

        t0 = time.time()
        n = naive_rag(q)
        dt_n = time.time() - t0
        print(f"📎 Naive  ({dt_n:.1f}s):{n}")
        print("-" * 64)


if __name__ == "__main__":
    main()
