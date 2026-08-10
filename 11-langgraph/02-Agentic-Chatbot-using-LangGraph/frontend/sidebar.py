import streamlit as st

from frontend.hitl import sync_pending_interrupt
from frontend.session import load_conversation, messages_to_ui_history, reset_chat


def render_sidebar() -> None:
    st.sidebar.title("My Conversations")

    if st.sidebar.button("New Chat"):
        reset_chat()
        st.rerun()

    for thread_id in st.session_state["chat_threads"][::-1]:
        if st.sidebar.button(str(thread_id), key=thread_id):
            st.session_state["thread_id"] = thread_id
            messages = load_conversation(thread_id)
            st.session_state["message_history"] = messages_to_ui_history(messages)
            sync_pending_interrupt(thread_id)
            st.rerun()
