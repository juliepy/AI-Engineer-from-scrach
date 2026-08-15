# 人工智能 Agent 方向面试宝典（代码示例）
B站：https://space.bilibili.com/524275099

面向 Agent / RAG / 多智能体面试的代码与笔记仓库，按主题分目录，可直接跑示例。后半段转向开源 Agent 源码精读与工程化。

## 目录

| 目录 | 内容 |
|------|------|
| `00-大纲` | 教学大纲 |
| `01-Agent` | Function Call、ReAct、Plan-and-Execute、Reflexion、LATS、Multi-Agent |
| `02-RAG` | 简单 RAG → 进阶 → 评测 → PDF 解析 → Agentic RAG |
| `03-memory` | 窗口记忆、长期记忆、摘要记忆、三因子打分 |
| `04-multiagent` | 多智能体架构与协作模式 |
| `05-model-route` | 模型路由 |
| `06-harnes` | Harness / Agent 工程化实践 |
| `07-llm_from_scrach` | 从零实现 LLM |
| `08-hermes-agent` | Hermes 源码精读：Memory、主循环、Eval、Prompt、环境、Cron、Gateway |
| `09-loop-engineering` | Loop Engineering：Prompt → Context → Harness → Loop |
| `10-CICD` | CI/CD 面试突击：pytest、GitLab CI、排查、Jenkins |
| `11-langgraph` | LangGraph 多智能体：课程、Chatbot、TripMate 旅行规划 |
| `12-hermes-agent-small` | waku：本地优先教学助手（Harness · Loop · Memory · Eval） |
| `13-pi-agent` | Pi 架构与上手：Core / Interactive、会话树、扩展与 Skills |
| `99-My idea` | 个人笔记与扩展思考 |

## 学习路径

基础概念 → Prompt / 工具调用 → RAG → 记忆 → 多智能体 → 模型路由 → Harness → 大模型基础 → **开源 Agent 源码（Hermes / waku / Pi）** → Loop Engineering → CI/CD → LangGraph。

源码精读建议：先 `08-hermes-agent` 建立 Runtime 心智模型，再用 `12-hermes-agent-small`（waku）看精简四支柱，最后用 `13-pi-agent` 对照 TypeScript 的 Core / Interactive 拆分。

## 使用说明

各子目录多为独立 demo（`.py` / `.ipynb`），进入对应目录按其中 README 或依赖文件安装即可。根目录可使用 `.venv` 与 `.env` 配置 API Key。

- `08` / `12` / `13` 以笔记 + 对照源码为主；`12-hermes-agent-small` 可按该目录 `README.md` 本地跑起来。
- Pi 上手与架构见 `13-pi-agent/00-learn-guide.md`、`13-pi-agent/01-arch.md`。
