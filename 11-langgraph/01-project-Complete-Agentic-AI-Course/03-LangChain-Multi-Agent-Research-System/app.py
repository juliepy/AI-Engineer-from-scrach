import streamlit as st
import time
from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="多智能体研究助手",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PIPELINE_STEPS = ("search", "reader", "writer", "critic")

STEP_META = {
    "search": ("01", "搜索智能体", "检索近期可靠的网页信息"),
    "reader": ("02", "阅读智能体", "抓取并抽取网页正文"),
    "writer": ("03", "写作链路", "撰写完整研究报告"),
    "critic": ("04", "评审链路", "评估报告并打分"),
}

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    color: #edf3ff;
}

.stApp {
    background: #07111f;
    background-image:
        radial-gradient(circle at top left, rgba(0,191,255,0.14), transparent 32%),
        radial-gradient(circle at bottom right, rgba(124,58,237,0.12), transparent 30%),
        linear-gradient(180deg, #07111f 0%, #0a1729 100%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f8fbff;
    margin: 0 0 1rem;
}
.hero h1 span {
    background: linear-gradient(135deg, #38bdf8, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #b5c3d9;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.65;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.35), transparent);
    margin: 2rem 0;
}

.stTextInput > div > div > input,
.stTextInput input {
    background: rgba(15, 23, 42, 0.95) !important;
    border: 1px solid rgba(56,189,248,0.4) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #38bdf8 !important;
    font-family: 'DM Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stTextInput > div > div > input::placeholder,
.stTextInput input::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
    opacity: 1 !important;
}
.stTextInput > div > div > input:focus,
.stTextInput input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 4px rgba(56,189,248,0.14) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #7dd3fc !important;
    font-weight: 500 !important;
}

/* Streamlit markdown / result text on dark bg */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
.stMarkdown strong, .stMarkdown em, .stMarkdown code,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: #f1f5f9 !important;
}
[data-testid="stMarkdownContainer"] a {
    color: #7dd3fc !important;
}
[data-testid="stMarkdownContainer"] code {
    background: rgba(255,255,255,0.08) !important;
    color: #e2e8f0 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #38bdf8 0%, #8b5cf6 100%) !important;
    color: white !important;
    font-family: 'Syne', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2.2rem !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 8px 30px rgba(56,189,248,0.22) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 12px 35px rgba(56,189,248,0.32) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

.step-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
    backdrop-filter: blur(10px);
}
.step-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56,189,248,0.18);
}
.step-card.active {
    border-color: rgba(56,189,248,0.65);
    background: rgba(56,189,248,0.12);
    box-shadow: 0 0 0 1px rgba(56,189,248,0.35), 0 0 28px rgba(56,189,248,0.22);
    transform: translateY(-2px) scale(1.02);
    animation: pulse-glow 1.6s ease-in-out infinite;
}
.step-card.done {
    border-color: rgba(34,197,94,0.28);
    background: rgba(34,197,94,0.05);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    border-radius: 18px 0 0 18px;
    background: rgba(255,255,255,0.06);
    transition: background 0.3s;
}
.step-card.active::before { background: #38bdf8; }
.step-card.done::before   { background: #22c55e; }

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 1px rgba(56,189,248,0.35), 0 0 18px rgba(56,189,248,0.18); }
    50%      { box-shadow: 0 0 0 2px rgba(56,189,248,0.55), 0 0 32px rgba(56,189,248,0.32); }
}

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #38bdf8;
    opacity: 0.85;
}
.step-title {
    font-family: 'Syne', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #f8fbff;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', 'PingFang SC', 'Microsoft YaHei', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
}
.status-waiting  { color: #64748b; }
.status-running  { color: #38bdf8; font-weight: 600; }
.status-done     { color: #22c55e; }

.result-panel {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 18px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #7dd3fc;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(56,189,248,0.25);
}
.result-content {
    font-size: 0.95rem;
    line-height: 1.85;
    color: #f8fafc !important;
    white-space: pre-wrap;
    font-family: 'DM Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.6rem;
}
.panel-label.orange {
    color: #7dd3fc;
    border-bottom: 1px solid rgba(56,189,248,0.25);
}
.panel-label.green {
    color: #4ade80;
    border-bottom: 1px solid rgba(34,197,94,0.25);
}

.stSpinner > div { color: #38bdf8 !important; }

details {
    background: rgba(255,255,255,0.02);
    border-radius: 14px;
    padding: 0.3rem 0.8rem;
    border: 1px solid rgba(255,255,255,0.06);
}
details summary {
    font-family: 'DM Mono', 'PingFang SC', 'Microsoft YaHei', monospace !important;
    font-size: 0.75rem !important;
    color: #b5c3d9 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

.section-heading {
    font-family: 'Syne', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #f8fbff;
    margin: 2rem 0 1rem;
}

.notice {
    font-family: 'DM Mono', 'PingFang SC', 'Microsoft YaHei', monospace;
    font-size: 0.72rem;
    color: #7f93ad;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("等待中", "status-waiting"),
        "running": ("● 进行中", "status-running"),
        "done":    ("✓ 已完成", "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    desc_html = (
        f"<div style='font-size:0.82rem;color:#94a3b8;margin-top:0.3rem;'>{desc}</div>"
        if desc else ""
    )
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def step_status(step: str) -> str:
    results = st.session_state.results
    if step in results:
        return "done"
    if st.session_state.running and st.session_state.current_step == step:
        return "running"
    return "waiting"


# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "results": {},
    "running": False,
    "done": False,
    "current_step": None,
    "topic_value": "",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">多智能体 AI 系统</div>
    <h1>研究<span>助手</span></h1>
    <p class="hero-sub">
        四个专用智能体协同完成搜索、抓取、写作与评审，
        针对任意主题自动生成研究报告。
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    topic = st.text_input(
        "研究主题",
        placeholder="例如：未来五年 AGI 发展路线图",
        key="topic_input",
        label_visibility="visible",
        disabled=st.session_state.running,
    )

    run_btn = st.button(
        "⚡ 启动研究流水线",
        use_container_width=True,
        disabled=st.session_state.running,
    )

    st.markdown("""
    <div style="margin:1rem 0 0.6rem;font-family:'DM Mono',monospace;font-size:0.68rem;color:#94a3b8;letter-spacing:0.1em;">
        试试这些 →
    </div>
    """, unsafe_allow_html=True)

    examples = [
        "大模型在科技行业的未来",
        "2026 年最新 AI Agent 盘点",
        "未来五年 AGI 发展路线图",
    ]
    ex_cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with ex_cols[i]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True, disabled=st.session_state.running):
                st.session_state.topic_input = ex
                st.rerun()

with col_pipeline:
    st.markdown('<div class="section-heading">流水线进度</div>', unsafe_allow_html=True)

    for step_key in PIPELINE_STEPS:
        num, title, desc = STEP_META[step_key]
        step_card(num, title, step_status(step_key), desc)


# ── Start pipeline ────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("请先输入研究主题。")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.current_step = "search"
        st.session_state.topic_value = topic.strip()
        st.rerun()


# ── Run one step per rerun（便于当前步骤高亮）────────────────────────────────
if st.session_state.running and not st.session_state.done:
    results = dict(st.session_state.results)
    topic_val = st.session_state.topic_value
    current = st.session_state.current_step

    if current == "search":
        with st.spinner("🔍 搜索智能体工作中…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [
                    ("user", f"Find recent, reliable and detailed information about: {topic_val}")
                ]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = results
            st.session_state.current_step = "reader"
            st.rerun()

    elif current == "reader":
        with st.spinner("📄 阅读智能体正在抓取内容…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [(
                    "user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                )]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = results
            st.session_state.current_step = "writer"
            st.rerun()

    elif current == "writer":
        with st.spinner("✍️ 写作链路正在起草报告…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined,
            })
            st.session_state.results = results
            st.session_state.current_step = "critic"
            st.rerun()

    elif current == "critic":
        with st.spinner("🧐 评审链路正在审阅报告…"):
            results["critic"] = critic_chain.invoke({
                "report": results["writer"]
            })
            st.session_state.results = results
            st.session_state.running = False
            st.session_state.done = True
            st.session_state.current_step = None
            st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">研究结果</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 搜索结果（原始）", expanded=False):
            st.markdown(f"""
            <div class="result-panel">
                <div class="result-panel-title">搜索智能体输出</div>
                <div class="result-content">{r["search"]}</div>
            </div>
            """, unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 抓取内容（原始）", expanded=False):
            st.markdown(f"""
            <div class="result-panel">
                <div class="result-panel-title">阅读智能体输出</div>
                <div class="result-content">{r["reader"]}</div>
            </div>
            """, unsafe_allow_html=True)

    if "writer" in r:
        st.markdown(
            '<div class="panel-label orange">📝 最终研究报告</div>',
            unsafe_allow_html=True,
        )
        st.markdown(r["writer"])
        st.download_button(
            label="⬇ 下载报告（.md）",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown(
            '<div class="panel-label green">🧐 评审反馈</div>',
            unsafe_allow_html=True,
        )
        st.markdown(r["critic"])


st.markdown("""
<div class="notice">
    研究助手 · 基于 LangChain 多智能体流水线 · Streamlit 构建
</div>
""", unsafe_allow_html=True)
