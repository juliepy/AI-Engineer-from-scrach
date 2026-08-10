# Agentic Chatbot with LangGraph （包含完整的框架和 human in the loop）

基于 **LangGraph + Streamlit** 的 Agentic 聊天机器人。

- **LLM**：`deepseek-v4-pro`（DeepSeek OpenAI 兼容 API）
- **Embedding**：`sentence-transformers` 加载 `BAAI/bge-small-en-v1.5`（首次下载到 `models/`，之后本地加载）
- **能力**：网页搜索 · 天气 · 股票行情 · PDF RAG · 计算器 · 股票购买 HITL 审批
- **记忆**：SQLite Checkpointer，多会话线程可切换恢复

---

## Quick Start

### 1. 环境准备（推荐 Windows 原生）

```bash
cd 02-Agentic-Chatbot-using-LangGraph

# 若目录里还有 WSL 建的 .venv，先删掉或改名后再建 Windows venv
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env`：

```env
DEEPSEEK_API_KEY=your-deepseek-api-key
TAVILY_API_KEY=your-tavily-api-key

# optional
# DEEPSEEK_BASE_URL=https://api.deepseek.com
# EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
# LOCAL_EMBEDDING_MODEL_DIR=models/bge-small-en-v1.5
# LOG_LEVEL=INFO                                 # DEBUG / INFO / WARNING / ERROR
# LOG_DIR=logs
```

> 天气工具复用 `TAVILY_API_KEY`，通过 Tavily 搜索获取实时天气。

> Embedding **懒加载**：普通聊天不加载 `torch`；首次上传 PDF / 调用 RAG 时才会加载。  
> 权重目录：`models/bge-small-en-v1.5/`（可提前：`python scripts/download_embedding_model.py`）。  
> 若更换过 embedding 模型，请删除本地 `data/faiss_db/` 后重新上传 PDF。  
> 运行日志：`logs/agentic-chatbot.log`；启动分段计时：`logs/startup.log`。

### 3. 启动应用

```bash
python -m streamlit run app.py
```

浏览器打开 **`http://127.0.0.1:8501`**。  
终端出现 URL 后，第一次打开页面仍会花几秒导入 LangGraph（正常）；同一进程内刷新会快很多。  
若白屏：清掉该站点 Cookie / 站点数据后硬刷新。

---

## 目录结构

```text
02-Agentic-Chatbot-using-LangGraph/
├── app.py                         # Streamlit 入口
├── requirements.txt
├── README.md
├── data/                          # 运行时数据（gitignore）
│   ├── chatbot.db                 # LangGraph SQLite checkpointer
│   └── faiss_db/                  # PDF RAG 向量库
├── backend/                       # LangGraph 后端
│   ├── __init__.py                # 导出 chatbot / get_all_threads / ingest_rag_document
│   ├── logger.py                  # 统一日志（控制台 + 滚动文件）
│   ├── llm.py                     # DeepSeek LLM + SentenceTransformer Embeddings
│   ├── rag.py                     # PDF 入库、检索、rag_tool
│   ├── graph.py                   # StateGraph / nodes / checkpointer
│   ├── threads.py                 # 会话线程列表
│   └── tools/                     # 工具包（按能力拆分）
│       ├── __init__.py            # 汇总 tools / llm_with_tools
│       ├── search.py              # Tavily 搜索
│       ├── calculator.py          # 数学计算
│       ├── stock.py               # 股价查询 + HITL 购买
│       └── weather.py             # Tavily 天气检索
└── frontend/                      # Streamlit 前端
    ├── __init__.py
    ├── session.py                 # session / thread 管理
    ├── hitl.py                    # interrupt 同步与 resume
    ├── sidebar.py                 # 侧边栏会话列表
    └── chat.py                    # 消息流、审批 UI、PDF 上传
```

---

## 系统逻辑

### 整体架构

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'fontFamily': 'Inter, "Segoe UI", system-ui, sans-serif',
    'background': '#1C1F24',
    'primaryColor': '#3D4F5F',
    'primaryTextColor': '#E8E6E3',
    'primaryBorderColor': '#7A91A8',
    'secondaryColor': '#4A3F42',
    'tertiaryColor': '#4A453C',
    'lineColor': '#9AABB8',
    'textColor': '#E8E6E3',
    'mainBkg': '#2A3038',
    'nodeBorder': '#7A91A8',
    'clusterBkg': '#24292F',
    'clusterBorder': '#6B7C8A',
    'titleColor': '#D4C4A8',
    'edgeLabelBackground': '#2A3038',
    'tertiaryTextColor': '#D4C4A8'
  }
}}%%

flowchart TB
    User(["👤 User"])

    subgraph FE["🖥️ Frontend · Streamlit"]
        direction TB
        App["app.py"]
        Sidebar["sidebar.py"]
        Chat["chat.py"]
        HITL_UI["hitl.py"]
    end

    subgraph BE["⚙️ Backend · LangGraph"]
        direction TB
        Graph["graph.py"]
        ChatNode["chat_node<br/>deepseek-v4-pro"]
        ToolNode["ToolNode"]
        CKPT[("SQLite checkpointer")]
        RAG["rag.py + FAISS<br/>bge-small-en-v1.5"]
    end

    subgraph TOOLS["🧰 backend/tools"]
        direction LR
        T1["search.py"] ~~~ T2["calculator.py"] ~~~ T3["stock.py"] ~~~ T4["weather.py"] ~~~ T5["rag_tool"]
    end

    User --> App
    App --> Sidebar
    App --> Chat
    App --> HITL_UI
    Chat --> Graph
    HITL_UI --> Graph
    Graph --> ChatNode
    ChatNode -->|need tools| ToolNode
    ToolNode --> TOOLS
    T5 --> RAG
    ToolNode --> ChatNode
    ChatNode -->|final answer| Chat
    Graph <--> CKPT
    ChatNode -.->|interrupt| HITL_UI

    linkStyle default stroke:#9AABB8,stroke-width:1.5px,color:#D4C4A8

    classDef user fill:#4A3F42,stroke:#C4A7A7,stroke-width:1.5px,color:#F0E6E6
    classDef fe fill:#3D4F5F,stroke:#7A91A8,stroke-width:1.5px,color:#E4ECF2
    classDef be fill:#36424D,stroke:#8FA3B5,stroke-width:1.5px,color:#E4ECF2
    classDef tool fill:#4A453C,stroke:#C9B896,stroke-width:1.5px,color:#F2EBDD
    classDef store fill:#423A40,stroke:#B89B9B,stroke-width:1.5px,color:#F0E6E6

    class User user
    class App,Sidebar,Chat,HITL_UI fe
    class Graph,ChatNode,ToolNode,RAG be
    class T1,T2,T3,T4,T5 tool
    class CKPT store
```

### Agent 运行时序

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'background': '#1C1F24',
    'actorBkg': '#3D4F5F',
    'actorBorder': '#7A91A8',
    'actorTextColor': '#E8E6E3',
    'signalColor': '#9AABB8',
    'signalTextColor': '#D4C4A8',
    'labelBoxBkgColor': '#2A3038',
    'labelBoxBorderColor': '#7A91A8',
    'labelTextColor': '#D4C4A8',
    'noteBkgColor': '#4A453C',
    'noteBorderColor': '#C9B896',
    'noteTextColor': '#F2EBDD',
    'activationBkgColor': '#36424D',
    'activationBorderColor': '#8FA3B5',
    'sequenceNumberColor': '#1C1F24'
  }
}}%%

sequenceDiagram
    autonumber
    actor U as User
    participant UI as Streamlit UI
    participant G as LangGraph
    participant L as deepseek-v4-pro
    participant T as Tools
    participant H as HITL Panel

    U->>UI: 输入问题 / 上传 PDF
    alt 上传 PDF
        UI->>G: ingest_rag_document()
        Note over G: 本地 BGE embedding → FAISS
    end

    UI->>G: stream(HumanMessage)
    G->>L: 推理是否需要工具

    alt 需要工具
        L->>T: tool_calls
        alt purchase_stock HITL
            T-->>G: interrupt(审批提示)
            G-->>UI: pending_hitl
            UI->>H: Approve / Reject
            U->>H: 审批决策
            H->>G: Command(resume=yes/no)
            G->>T: 继续执行
            T-->>L: 工具结果
        else 其他工具
            T-->>L: 工具结果
        end
        L-->>UI: 流式最终回答
    else 直接回答
        L-->>UI: 流式最终回答
    end

    UI-->>U: 渲染回复 & 会话记忆
```

### Function Call Flow（文本）

前后端同进程：Streamlit `frontend/*` 直接 `import` 并调用 `backend` 导出函数，无 HTTP。

**1. 启动渲染**

```text
app.py
├── init_session_state()                    # frontend/session.py
│   ├── generate_thread_id()
│   ├── get_all_threads()                   # backend/threads.py → checkpointer
│   └── add_thread(thread_id)
├── sync_pending_interrupt(thread_id)       # frontend/hitl.py
│   └── get_pending_interrupt(thread_id)
│       └── chatbot.get_state(config)       # backend.graph 编译图
├── render_sidebar()                        # frontend/sidebar.py
├── render_message_history()                # frontend/chat.py
├── render_hitl_approval()                  # frontend/chat.py
└── handle_chat_input()                     # frontend/chat.py
```

**2. 用户发消息（主路径）**

```text
handle_chat_input()
└── _stream_assistant_response(user_input)
    └── chatbot.stream(
            {"messages": [HumanMessage(...)]},
            config={"configurable": {"thread_id": ...}},
            stream_mode="messages",
        )                                   # backend/graph.py → compiled graph
        ├── chat_node(state)
        │   └── llm_with_tools.invoke(messages)
        │       ├── 无 tool_calls → 流式 AIMessage → st.write_stream
        │       └── 有 tool_calls → tools_condition → tools
        └── tools (ToolNode)
            ├── search_tool / calculator / get_stock_price /
            │   get_current_weather / rag_tool / purchase_stock
            ├── purchase_stock → interrupt(...)   # HITL 暂停
            └── 工具结果回灌 chat_node → 最终 AIMessage
    └── get_pending_interrupt(thread_id)    # 若有 interrupt
        └── save_pending_interrupt(...)     # 写入 st.session_state["pending_hitl"]
```

**3. 上传 PDF**

```text
handle_chat_input()
└── _process_uploaded_pdf(uploaded_pdf)
    └── ingest_rag_document(temp_path)      # backend/rag.py
        ├── 解析 PDF → chunks
        ├── get_embeddings()                # backend/llm.py · BGE 本地
        └── FAISS 写入 data/faiss_db/
```

**4. HITL 审批恢复**

```text
render_hitl_approval()
└── resume_hitl_execution("yes" | "no")     # frontend/hitl.py
    └── chatbot.stream(
            Command(resume=decision),
            config=...,
            stream_mode="messages",
        )
        └── 从 interrupt 处继续 ToolNode
            → purchase_stock 返回结果
            → chat_node 生成最终回答
            → st.write_stream / st.rerun()
```

**5. 切换 / 新建会话**

```text
# New Chat
render_sidebar() → reset_chat() → generate_thread_id() + 清空 history/HITL

# 点击已有 thread
render_sidebar()
├── load_conversation(thread_id)            # chatbot.get_state → messages
├── messages_to_ui_history(messages)
└── sync_pending_interrupt(thread_id)       # 恢复该线程未完成审批
```

### LangGraph 状态机

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'background': '#1C1F24',
    'primaryColor': '#3D4F5F',
    'primaryTextColor': '#E8E6E3',
    'primaryBorderColor': '#7A91A8',
    'lineColor': '#9AABB8',
    'textColor': '#D4C4A8',
    'labelColor': '#D4C4A8',
    'tertiaryTextColor': '#D4C4A8',
    'edgeLabelBackground': '#2A3038',
    'noteBkgColor': '#4A3F42',
    'noteTextColor': '#F0E6E6',
    'noteBorderColor': '#C4A7A7'
  }
}}%%

stateDiagram-v2
    [*] --> chat_node: START

    chat_node --> tools: tools_condition / 有 tool_calls
    chat_node --> [*]: 无 tool_calls / 结束本轮

    tools --> chat_node: 工具结果回灌

    note right of tools
      stock.purchase_stock 触发
      interrupt → 等待人工审批
      resume 后继续
    end note
```
