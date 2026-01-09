import streamlit as st
import time
from typing import List, Tuple
import requests

# -----------------------------
# API Configuration
# -----------------------------
API_URL = "http://127.0.0.1:8000/get-response"


# -----------------------------
# Stream helpers
# -----------------------------
def stream_response(text: str):
    for word in text.split():
        yield word + " "
        time.sleep(0.02)


# -----------------------------
# App setup
# -----------------------------
st.set_page_config(page_title="Libris", page_icon="📚")
st.title("📚 Libris")

st.sidebar.markdown("### Knowledge Base")
st.sidebar.markdown("Collection: `knowledge_chunks`")
st.sidebar.markdown("Mode: 🔍 Search-only")


# -----------------------------
# Session state
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# Chat input
# -----------------------------
if prompt := st.chat_input("Ask a question about the knowledge base"):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # -------------------------
    # API Call
    # -------------------------
    try:
        response = requests.post(API_URL, json={"query": prompt})
        response.raise_for_status()
        answer = response.json().get("answer", "No answer returned.")
    except requests.exceptions.RequestException as e:
        answer = f"Error: {e}"

    # Assistant message
    with st.chat_message("assistant"):
        st.markdown(answer)  # Render markdown-formatted response

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
