#小白 AI Agent 学习指南

自下往上叠：底层基础撑起能力，能力撑起记忆与 Harness，最上才是模型与评测。

```mermaid
%%{init: {"theme": "dark", "flowchart": {"curve": "linear", "rankSpacing": 48, "nodeSpacing": 24, "padding": 24, "useMaxWidth": false, "htmlLabels": true, "titleTopMargin": 40, "subGraphTitleMargin": {"top": 8, "bottom": 20}}, "themeVariables": {"fontSize": "22px", "background": "#000000", "lineColor": "#CBD5E1", "clusterBkg": "#111111", "clusterBorder": "#C4B5FD", "titleColor": "#FDE68A", "edgeLabelBackground": "#111111"}, "themeCSS": ".nodeLabel,.label,.cluster-label,span{font-size:22px!important}"}}%%
flowchart TB
    subgraph row4Layer[" "]
        direction LR
        L4["模型"]
        ML["Model Layer<br/>模型层<br/>开源权重·Fine-Tune·QLoRA"]
        OE["Observability<br/>可观测与评估<br/>评测·护栏·红队"]
        L4 ~~~ ML ~~~ OE
    end

    subgraph row3Layer[" "]
        direction LR
        L3["运行时"]
        MS["Memory System<br/>记忆系统<br/>STM/LTM·Mem0·会话"]
        HE["Harness<br/>Harness工程<br/>Hook·工具循环·沙箱"]
        L3 ~~~ MS ~~~ HE
    end

    subgraph row2Layer[" "]
        direction LR
        L2["能力"]
        CAP["Capability<br/>能力层/MCP<br/>Function Call·Tool·MCP"]
        AC["Agent Core<br/>Agent核心<br/>ReAct·SDK·从零构建"]
        MA["Multi-Agent<br/>多智能体编排<br/>LangGraph·A2A"]
        L2 ~~~ CAP ~~~ AC ~~~ MA
    end

    subgraph row1Layer[" "]
        direction LR
        L1["基础"]
        FL["Foundation<br/>底层基础<br/>GenAI·LLM API·Transformer"]
        CE["Context<br/>上下文工程<br/>Prompt·上下文·结构化输出"]
        RAG["RAG<br/>检索增强生成<br/>Embedding·向量库·Pipeline"]
        L1 ~~~ FL ~~~ CE ~~~ RAG
    end

    L4 --> L3 --> L2 --> L1

    classDef start fill:#BFDBFE,stroke:#93C5FD,color:#1E3A8A,font-size:22px
    classDef step fill:#A5F3FC,stroke:#67E8F9,color:#155E75,font-size:22px
    classDef dec fill:#FEF08A,stroke:#FDE047,color:#713F12,font-size:22px
    classDef prod fill:#E9D5FF,stroke:#D8B4FE,color:#6B21A8,font-size:22px
    classDef bad fill:#FBCFE8,stroke:#F9A8D4,color:#831843,font-size:22px
    classDef ok fill:#BBF7D0,stroke:#86EFAC,color:#14532D,font-size:22px
    classDef wrap fill:#111111,stroke:#C4B5FD,color:#FDE68A,font-size:22px

    class FL,OE start
    class CAP,RAG step
    class ML,MA dec
    class CE,HE prod
    class MS bad
    class AC ok
    class L4,L3,L2,L1 wrap
```

## 本仓库学习路线

对照上面四层读 `Readme.md`。目录编号是写作顺序，真正学的时候先走概念，再上工程，源码按 Hermes → waku → Pi，最后用 Loop / CI/CD / LangGraph 收口。

```text
function flow（仓库路线）
  00 大纲
    → 01 范式 → 02 RAG → 03 Memory → 04 多智能体 → 05 路由
    → 06 Harness → 07 LLM基础
    → 08 Hermes → 12 waku → 13 Pi
    → 09 Loop工程 → 10 CI/CD → 11 LangGraph
```
