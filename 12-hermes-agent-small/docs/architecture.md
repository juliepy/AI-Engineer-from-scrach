# Architecture — the whiteboard, refreshed

The same system as the two whiteboard diagrams from the previous videos
(the generic Harness/Loop/Memory/LLM-Ops one and the Hermes-specific one),
now with a file path on every box.

```mermaid
flowchart TB
    subgraph GW["Gateway Interface — waku/gateway/"]
        CLI["cli.py (default)"]
        TG["telegram.py (optional)"]
    end

    subgraph RUN["Ephemeral Agent Run — everything here is rebuilt per turn"]
        WM["Working Memory — runtime/session.py<br/>SOUL.md + memory context + chat history"]
        subgraph LOOP["The Loop — loop/agent.py"]
            LLM["LLM call<br/>(loop/models.py)"]
            TOOLS["Tools — tools/<br/>create_event · save_note · send_message"]
            LLM -->|tool calls| TOOLS -->|results| LLM
        end
        WM --> LLM
        GUARD["end-loop guardrails:<br/>no-tool-call exit · max iterations"]
    end

    GW --> WM
    LLM -->|reply| GW

    subgraph MEM["Memory — waku/memory/"]
        GATE{{"retrieval_gate.py<br/>'does this turn need memory?'"}}
        PROC["procedural/ — SKILL.md<br/>how to act"]
        SEM["semantic/ — facts (FTS5,<br/>or Supabase pgvector)"]
        EPI["episodic/ — dated events"]
        CONS{{"consolidation.py<br/>'only after N new chats'"}}
        DB[("state.db — one SQLite file")]
    end

    WM -.->|every turn| GATE
    GATE -->|only if needed| SEM & EPI
    PROC -->|on keyword match| WM
    GW -->|save messages| DB
    CONS -->|distill into facts| SEM
    CONS -->|one episode| EPI
    SEM & EPI --- DB

    subgraph OPS["LLM Ops — waku/ops/ + evals/"]
        TRACE["tracing.py — 1 trace/run<br/>JSONL always · OTel → Phoenix/Langfuse"]
        DET["evals/deterministic — 0/1<br/>'did the right tool fire?'"]
        JUDGE["evals/judge — scored %<br/>'was the reply good?'"]
        RGATE{{"release_gate.py"}}
        TRACE --> DET & JUDGE --> RGATE -->|eval passed| SHIP["release: new prompt/<br/>model/config version"]
    end

    RUN -.->|every event| TRACE

    %% 讲课高对比莫兰迪：浅底 + 深字 + 粗描边
    classDef gateway fill:#C5D5E4,stroke:#2F4A63,color:#14202C,stroke-width:3px
    classDef working fill:#E8DCC8,stroke:#5C4630,color:#1F1710,stroke-width:3px
    classDef loopNode fill:#B7CBDC,stroke:#2A455C,color:#14202C,stroke-width:3px
    classDef tools fill:#C9D8E3,stroke:#35566F,color:#14202C,stroke-width:3px
    classDef gate fill:#EAD9B8,stroke:#6A5230,color:#1F1710,stroke-width:3px
    classDef memory fill:#E4CCC6,stroke:#6B3F44,color:#241618,stroke-width:3px
    classDef consolidate fill:#E6CED4,stroke:#6E404C,color:#241618,stroke-width:3px
    classDef ops fill:#D5DBE0,stroke:#2F3A42,color:#14191E,stroke-width:3px
    classDef gwBox fill:#EEF3F7,stroke:#2F4A63,color:#14202C,stroke-width:3px
    classDef runBox fill:#F6F0E6,stroke:#5C4630,color:#1F1710,stroke-width:3px
    classDef loopBox fill:#EEF3F7,stroke:#2F4A63,color:#14202C,stroke-width:3px
    classDef memBox fill:#F7EEEC,stroke:#6B3F44,color:#241618,stroke-width:3px
    classDef opsBox fill:#EFF1F3,stroke:#2F3A42,color:#14191E,stroke-width:3px

    class CLI,TG gateway
    class WM working
    class LLM,GUARD loopNode
    class TOOLS tools
    class GATE gate
    class PROC,SEM,EPI,DB memory
    class CONS consolidate
    class TRACE,DET,JUDGE,RGATE,SHIP ops
    class GW gwBox
    class RUN runBox
    class LOOP loopBox
    class MEM memBox
    class OPS opsBox
```

## Design decisions worth stealing

- **The gate before retrieval** (not retrieval on every turn): a cheap-model judge
  answers "does this message need the user's memory?" — saves latency and, more
  importantly, keeps irrelevant memories from biasing answers.
- **Consolidation is batched** ("after N chats"), asynchronous to the reply path,
  and loss-safe: if the summarizer fails, the chat log stays unconsolidated.
- **Deterministic evals and judge evals never mix.** One is a unit test, the other
  is a scored opinion. The release gate requires 100% of the first and a threshold
  on the second.
- **Every layer has a boring default and a documented upgrade** — FTS5 → pgvector,
  mock calendar → Google Calendar, JSONL → Phoenix/Langfuse. The default is always
  zero-signup.

## What this deliberately is not

Not a framework, not multi-agent, not production. It's the readable blueprint —
OpenClaw and Hermes are the products; this is the afternoon read that explains them.
