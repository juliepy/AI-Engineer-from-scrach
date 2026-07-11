#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现场演示 · Agentic RAG(为讲台优化)
=====================================
对应课件第 16 页 🎬 现场演示,分三幕展示:
  幕1  简单问候   → Agent 判断"不需要检索",直接答(比 Naive 更快)
  幕2  跨域复杂   → Agent 在 product / policy / tickets 三个向量库间路由,多次检索
  幕3  检索超时   → 降级到 LLM 直答,并标注"未经文档验证"(fallback)
全程可接 LangSmith,产出完整 Trace。

两种运行模式:
  • 真实模式(接 LLM,现场展示真决策)
  • --mock 模式(离线、脚本化、100% 跑通)—— 网络/额度出问题时的保命备份

用法见文件末尾,或运行:  python3 agentic_rag_demo.py --help
"""

import os
import re
import sys
import json
import time
import argparse

# ---------- 终端配色(讲台上看得清) ----------
C = {"th": "\033[94m", "ac": "\033[93m", "ob": "\033[96m", "ok": "\033[92m",
     "no": "\033[91m", "dim": "\033[2m", "b": "\033[1m", "e": "\033[0m"}

def say(s=""): print(s)
def rule(): say(C["dim"] + "─" * 66 + C["e"])
def pause(interactive):
    if interactive:
        input(C["dim"] + "   〔按回车继续〕" + C["e"])

# ============================================================
# 三个向量库(多库路由的主角)
# ============================================================
VECTOR_STORES = {
    "product": ["ISA 支持关键词、向量、混合三种检索模式。",
                "ISA 向量库默认返回 top-5,可用 top_k 调整。"],
    "policy":  ["退款政策:购买后 14 天内可全额退款,需订单号。",
                "数据合规:用户 PII 必须脱敏后才能写入日志。"],
    "tickets": ["工单#1024:检索慢,已通过增大缓存 + top_k 解决。"],
}

def _score(q, t):
    # 字符级重叠打分(对中文更稳),真实中换成向量相似度
    qs = set(q.lower()) - set(" 的了吗呢啊")
    ts = set(t.lower())
    return round(len(qs & ts) / (len(qs) + 1e-9), 3)

# 用于"幕3"演示:把这个库标记为会超时
TIMEOUT_STORE = {"name": None}

def search_docs(query, store="product", top_k=3):
    if TIMEOUT_STORE["name"] == store:                 # 故意触发超时(演示 fallback)
        time.sleep(0.4)
        raise TimeoutError(f"向量库 {store} 检索超时")
    # 向量检索总会返回最近邻(即使得分不高),按相关性排序取 top_k
    hits = sorted(({"text": t, "score": _score(query, t)} for t in VECTOR_STORES.get(store, [])),
                  key=lambda d: d["score"], reverse=True)[:top_k]
    return {"status": "ok" if hits else "empty", "store": store, "results": hits}

def search_web(query):
    time.sleep(0.2)
    return {"status": "ok", "results": [f"[web] 关于「{query}」的公开摘要 …"]}

# ============================================================
# LLM 决策 —— 真实模式 vs mock 模式
# ============================================================
SYSTEM_PROMPT = (
    "你是 ISA 知识助手。简单寒暄直接答不检索;需要内部知识调 search_docs 并选对库"
    "(product/policy/tickets),跨域可多次检索;不够补 search_web;找不到就照实说,不编造。"
)

def real_llm_decider():
    """返回一个 decide(messages)->dict 的函数,真正调用 OpenAI 的 tool calling。"""
    from openai import OpenAI
    client = OpenAI()
    try:
        from langsmith.wrappers import wrap_openai
        client = wrap_openai(client)                    # LangSmith 自动追踪
    except Exception:
        pass
    schema = [{"type": "function", "function": {
        "name": "search_docs", "description": "搜内部文档,store∈product/policy/tickets,可多次",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}, "store": {"type": "string"}}, "required": ["query", "store"]}}},
        {"type": "function", "function": {"name": "search_web", "description": "网页搜索",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}}]
    def decide(messages):
        r = client.chat.completions.create(model="gpt-4o", messages=messages,
                                           tools=schema, temperature=0).choices[0].message
        if r.tool_calls:
            return {"type": "tools", "calls": [(c.function.name, json.loads(c.function.arguments), c.id)
                                               for c in r.tool_calls], "raw": r}
        return {"type": "final", "text": r.content}
    return decide

def mock_decider():
    """离线脚本化决策:根据问题关键词模拟 Agent 的路由,保证 100% 跑通(保命备份)。"""
    def decide(messages):
        # 稳健地取出用户问题(多轮后 messages 会变长)
        q = next((m["content"] for m in messages if isinstance(m, dict) and m.get("role") == "user"), "")
        seen = [m for m in messages if isinstance(m, dict) and m.get("role") == "tool"]
        cross = ("对比" in q or "区别" in q)     # 是否跨域问题

        # 幕1:寒暄 → 不检索
        if any(w in q for w in ["你好", "谢谢", "hi", "hello"]):
            return {"type": "final", "text": "你好!有什么可以帮你的?(未调用任何工具)"}

        # 幕3:超时库 → 第一次尝试就打到会超时的库,触发降级
        if TIMEOUT_STORE["name"] and not seen:
            return {"type": "tools", "calls": [("search_docs", {"query": q, "store": TIMEOUT_STORE["name"]}, "c1")]}

        # 幕2:跨域 → 先搜 product,再补搜 policy,最后综合作答
        if cross:
            if not seen:
                return {"type": "tools", "calls": [("search_docs", {"query": q, "store": "product"}, "c1")]}
            if len(seen) == 1:
                return {"type": "tools", "calls": [("search_docs", {"query": q, "store": "policy"}, "c2")]}
        else:
            # 单域 → 按关键词路由到单个库,搜一次即答
            store = "policy" if "退款" in q else "tickets" if ("工单" in q or "慢" in q) else "product"
            if not seen:
                return {"type": "tools", "calls": [("search_docs", {"query": q, "store": store}, "c1")]}

        # 综合已检索内容作答
        docs = []
        for m in seen:
            for r in json.loads(m["content"]).get("results", []):
                docs.append(r["text"])
        return {"type": "final", "text": "综合两个库的检索结果作答 → " + " | ".join(docs)}
    return decide

TOOLS = {"search_docs": search_docs, "search_web": search_web}

# ============================================================
# Agentic RAG 主循环(带 fallback / 降级)
# ============================================================
def agentic_rag(question, decide, interactive=False, max_steps=5):
    say(f"\n{C['b']}❓ 用户:{question}{C['e']}")
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]
    for step in range(max_steps):
        d = decide(messages)
        if d["type"] == "final":
            say(f"{C['ok']}✅ Final Answer:{C['e']} {d['text']}")
            return d["text"]
        messages.append(d.get("raw", {"role": "assistant", "tool_calls": "…"}))
        for name, args, cid in d["calls"]:
            say(f"{C['th']}  💭 Thought:{C['e']} 需要调用工具")
            say(f"{C['ac']}  ⚡ Action:{C['e']} {name}({args})")
            try:
                result = TOOLS[name](**args)
                say(f"{C['ob']}  👁 Observation:{C['e']} {json.dumps(result, ensure_ascii=False)}")
            except TimeoutError as e:
                # ★ fallback 降级:检索超时 → 直接用 LLM 回答并标注
                say(f"{C['no']}  ⏱ 检索超时:{e}{C['e']}")
                say(f"{C['no']}  ↳ 降级:改用 LLM 直接回答,标注「未经文档验证」{C['e']}")
                return "(未经文档验证)基于通用知识作答:请以官方文档为准。"
            result_json = json.dumps(result, ensure_ascii=False)
            messages.append({"role": "tool", "tool_call_id": cid, "content": result_json})
        pause(interactive)
    return "无法在有限步数内可靠回答,建议缩小问题范围。"

# ============================================================
# 三幕演示脚本
# ============================================================
def run_demo(decide, interactive):
    say(C["b"] + "\n🎬 Agentic RAG 现场演示 · 三幕" + C["e"])
    if os.getenv("LANGSMITH_TRACING") == "true":
        say(C["dim"] + "   ✅ LangSmith 追踪已开启,演示后去 dashboard 展开完整 Trace" + C["e"])

    say(C["b"] + "\n【幕1】简单问候 —— Agent 判断不需要检索" + C["e"]); rule()
    agentic_rag("你好", decide, interactive); rule(); pause(interactive)

    say(C["b"] + "\n【幕2】跨域复杂 —— Agent 在多个向量库间路由" + C["e"]); rule()
    agentic_rag("对比 ISA 的产品检索和退款政策各说了什么", decide, interactive); rule(); pause(interactive)

    say(C["b"] + "\n【幕3】检索超时 —— 触发 fallback 降级" + C["e"]); rule()
    TIMEOUT_STORE["name"] = "product"                     # 让 product 库超时
    agentic_rag("ISA 支持哪几种检索模式?", decide, interactive)
    TIMEOUT_STORE["name"] = None
    rule()
    say(C["ok"] + "\n演示结束。核心记忆点:多库路由 + 失败降级 + 全程 Trace。" + C["e"])

def main():
    p = argparse.ArgumentParser(description="Agentic RAG 现场演示")
    p.add_argument("--mock", action="store_true", help="离线脚本模式,不联网 100%% 跑通(保命备份)")
    p.add_argument("--step", action="store_true", help="每步暂停,方便逐幕讲解")
    args = p.parse_args()
    decide = mock_decider() if args.mock else real_llm_decider()
    if args.mock:
        say(C["dim"] + "（--mock 离线模式:决策为脚本化模拟,用于彩排 / 断网备份）" + C["e"])
    run_demo(decide, interactive=args.step)

if __name__ == "__main__":
    main()
