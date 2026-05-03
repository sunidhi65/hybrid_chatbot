import streamlit as st
import requests
import time
import uuid
import json
import os

st.markdown("""
<style>
button[kind="secondary"] {
    padding: 4px 8px !important;
    font-size: 12px !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Hybrid Chatbot", layout="wide")

STORE_FILE = "chat_store.json"

# Load chats
if os.path.exists(STORE_FILE):
    with open(STORE_FILE, "r") as f:
        all_chats = json.load(f)
else:
    all_chats = {}

# Fix format
for key in list(all_chats.keys()):
    if isinstance(all_chats[key], list):
        all_chats[key] = {"name": f"Chat {key[:4]}", "messages": all_chats[key]}

# Init chat
if not all_chats:
    new_id = str(uuid.uuid4())
    all_chats[new_id] = {"name": "Chat 1", "messages": []}

if "session_id" not in st.session_state:
    st.session_state.session_id = list(all_chats.keys())[0]

session_id = st.session_state.session_id

if "messages" not in st.session_state:
    st.session_state.messages = all_chats[session_id]["messages"]

# Prevent multiple generation
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# Sidebar
with st.sidebar:
    st.title("Hybrid Chatbot")

    if st.button("New Chat"):
        new_id = str(uuid.uuid4())
        all_chats[new_id] = {"name": f"Chat {len(all_chats)+1}", "messages": []}

        with open(STORE_FILE, "w") as f:
            json.dump(all_chats, f, indent=2)

        st.session_state.session_id = new_id
        st.session_state.messages = []
        st.rerun()

    for sid, chat_data in all_chats.items():
        if st.button(chat_data["name"], key=f"chat_{sid}"):
            st.session_state.session_id = sid
            st.session_state.messages = chat_data["messages"]
            st.rerun()

# Main UI
st.title("AI Chat Assistant")

# Show chat
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Assistant actions (clean UI)
        if msg["role"] == "assistant":
            col1, col2, col3 = st.columns([1,1,6])

            with col1:
                if st.button("Retry",key=f"retry_{i}", help="Regenerate", disabled=st.session_state.is_generating):
                    st.session_state.is_generating = True

                    st.session_state.messages.pop(i)
                
                    response = requests.post(
                        "http://127.0.0.1:8000/chat",
                        json={"messages": st.session_state.messages}
                    )

                    new_reply = response.json()["response"]

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": new_reply
                    })

                    st.session_state.is_generating = False
                    st.rerun()

            with col2:
                if st.button("Edit", key=f"edit_{i}", help="Edit previous prompt"):
                    st.session_state.edit_index = i - 1
                    st.session_state.edit_mode = True

# Edit mode
if st.session_state.get("edit_mode", False):

    idx = st.session_state.edit_index
    old_text = st.session_state.messages[idx]["content"]

    new_text = st.text_input("Edit message", value=old_text)

    if st.button("Submit Edit"):

        # Update user message
        st.session_state.messages[idx]["content"] = new_text

        # Remove everything AFTER this message
        st.session_state.messages = st.session_state.messages[:idx + 1]

        # Call API again
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"messages": st.session_state.messages}
        )

        new_reply = response.json()["response"]

        st.session_state.messages.append({
            "role": "assistant",
            "content": new_reply
        })

        st.session_state.edit_mode = False
        st.rerun()

# Input
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = requests.post(
        "http://127.0.0.1:8000/chat",
        json={"messages": st.session_state.messages}
    )

    data = response.json()

    st.session_state.messages.append({
        "role": "assistant",
        "content": data["response"]
    })

    all_chats[session_id]["messages"] = st.session_state.messages

    with open(STORE_FILE, "w") as f:
        json.dump(all_chats, f, indent=2)

    st.rerun()