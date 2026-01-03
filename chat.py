import streamlit as st
import json
import os
from datetime import datetime

CHAT_FILE = "chat_history.json"

def load_messages():
    if not os.path.exists(CHAT_FILE):
        return []
    with open(CHAT_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_message(username, text):
    messages = load_messages()
    new_msg = {
        "username": username,
        "text": text,
        "timestamp": datetime.now().strftime("%H:%M")
    }
    messages.append(new_msg)
    if len(messages) > 50: 
        messages = messages[-50:]
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f)

def app():
    st.header("Live Chat")

    if "username" not in st.session_state:
        st.session_state.username = "Anon"

    # Name change input
    col_name, col_status = st.columns([2, 4])
    with col_name:
        new_name = st.text_input("Name:", value=st.session_state.username, key="name_input")
        if new_name != st.session_state.username:
            st.session_state.username = new_name
            st.rerun()

    # Chat display
    messages = load_messages()
    with st.container(height=300):
        for msg in messages:
            if msg['username'] == st.session_state.username:
                st.markdown(f"**You:** {msg['text']}")
            else:
                st.markdown(f"**{msg['username']}:** {msg['text']}")

    # Chat Input
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([6, 1])
        with col_input:
            msg = st.text_input("Msg", label_visibility="collapsed", placeholder="Type message...")
        with col_btn:
            submitted = st.form_submit_button("Send")

        if submitted and msg:
            save_message(st.session_state.username, msg)
            st.rerun()

    if st.button("🔄 Check for New Messages"):
        st.rerun()