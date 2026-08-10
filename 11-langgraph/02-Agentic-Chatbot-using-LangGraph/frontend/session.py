import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from backend import chatbot, get_all_threads


def generate_thread_id() -> str:
    return str(uuid.uuid4())


def add_thread(thread_id: str) -> None:
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat() -> None:
    st.session_state["thread_id"] = generate_thread_id()
    st.session_state["message_history"] = []
    st.session_state["pending_hitl"] = None
    add_thread(st.session_state["thread_id"])


def load_conversation(thread_id: str) -> list:
    state = chatbot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        }
    )
    return state.values.get("messages", [])


def messages_to_ui_history(messages: list) -> list[dict]:
    temp_messages = []

    for message in messages:
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        else:
            continue

        temp_messages.append(
            {
                "role": role,
                "content": message.content,
            }
        )

    return temp_messages


def init_session_state() -> None:
    if "message_history" not in st.session_state:
        st.session_state["message_history"] = []

    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = generate_thread_id()

    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = get_all_threads()

    if "pending_hitl" not in st.session_state:
        st.session_state["pending_hitl"] = None

    add_thread(st.session_state["thread_id"])
