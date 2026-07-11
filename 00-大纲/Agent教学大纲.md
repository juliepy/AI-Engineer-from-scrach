# Agent 教学大纲

## 学习顺序

```
00-llm_function_call          工具调用入门
01-small-llm-function-call      Function Calling 小工程
02-Agent_react                  ReAct
02-Plan-and-Execute             规划与执行
03-Reflection                   反思重试
04-LATS                         树搜索
05-Multi-Agent-Crew             多角色协作（极简）
        ↓
multi-agent-arch                多 Agent 架构与框架
```

---

## multi-agent-arch

路径：`04-multiagent/multi-agent-arch/`

### 目录

```
multi-agent-arch/
├── 01_multi_agent_arch_demo.ipynb          # 架构模式：Pipeline / Hub-Spoke / Blackboard
├── 02_hierarchical_multi_agent_demo.ipynb  # 分层协作：Supervisor / HITL
├── 03_环境初始化与MAS基础.ipynb             # 环境配置 + MAS 概论
├── 04_autogen_实战.ipynb                   # AutoGen
├── 05_crewai_实战.ipynb                    # CrewAI
├── 06_agentic_rag_与框架对比.ipynb         # LangGraph + 框架选型
├── 07_课堂练习.ipynb                       # 综合练习
├── 08_工程化与总结.ipynb                   # 工程化最佳实践
├── 09_agent_ops_langsmith_demo.ipynb       # Agent Ops / LangSmith
├── multi_agent_frameworks_实战.ipynb       # 索引页（指向 03–08）
└── README.md
```

### 推荐顺序

```
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09
```
