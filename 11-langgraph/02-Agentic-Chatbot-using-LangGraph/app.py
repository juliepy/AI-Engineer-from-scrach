from backend.startup_log import startup_log

startup_log("[app] start")

import streamlit as st

from backend.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

st.set_page_config(
    page_title="Agentic Chatbot",
    page_icon="🤖",
)

st.title("Agentic Chatbot with LangGraph")
startup_log("[app] page shell rendered")

# Heavy imports (torch / sentence-transformers / langgraph) are slow on WSL+/mnt/d.
# Show UI first so the browser is not stuck on a blank page.
with st.spinner("Loading backend (models + LangGraph). First open may take 1–2 minutes..."):
    startup_log("[app] importing frontend modules ...")
    from frontend.chat import handle_chat_input, render_hitl_approval, render_message_history
    from frontend.hitl import sync_pending_interrupt
    from frontend.session import init_session_state
    from frontend.sidebar import render_sidebar

    startup_log("[app] all imports done")

logger.info("Rendering Streamlit app")
startup_log("[app] rendering UI ...")

init_session_state()
startup_log("[app] session ready")

sync_pending_interrupt(st.session_state["thread_id"])
startup_log("[app] hitl synced")

render_sidebar()
render_message_history()
render_hitl_approval()
handle_chat_input()
startup_log("[app] render complete")
