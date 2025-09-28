import os
import time
import json
import streamlit as st
from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="Coder Buddy", page_icon="⚡", layout="wide")

# --- Chatbot-like CSS ---
st.markdown("""
<style>
div.message {
    margin: 5px 0;
    padding: 8px 12px;
    border-radius: 12px;
    font-size: 16px;
    max-width: 75%;
    word-wrap: break-word;
}
div.user {
    background-color: #DCF8C6;
    text-align: right;
    margin-left: 25%;
}
div.agent {
    background-color: #F1F0F0;
    text-align: left;
    margin-right: 25%;
}
</style>
""", unsafe_allow_html=True)

# --- Initialize session ---
if 'current_session' not in st.session_state:
    st.session_state.current_session = []

def add_message(role, message):
    st.session_state.current_session.append({"role": role, "message": message})

# --- Display chat messages ---
def display_chat():
    for msg in st.session_state.current_session:
        css_class = "user" if msg["role"] == "User" else "agent"
        st.markdown(f"<div class='message {css_class}'>{msg['message']}</div>", unsafe_allow_html=True)

# --- User input ---
user_input = st.text_input("🚀 Enter your project request...", key="main_input")

if user_input and api_key:
    add_message("User", user_input)
    display_chat()

    planner = PlannerAgent(api_key)
    architect = ArchitectAgent(api_key)
    coder = CoderAgent(api_key)

    placeholder = st.empty()
    typed_text = ""

    # --- Generate Project Plan ---
    plan = planner.plan(user_input)
    add_message("Agent", plan)
    # Live printing for plan
    for char in plan:
        typed_text += char
        placeholder.markdown(f"<div class='message agent'>{typed_text}</div>", unsafe_allow_html=True)
        time.sleep(0.002)

    # --- Generate File Breakdown ---
    try:
        breakdown = architect.design(plan)
    except ValueError:
        breakdown = []

    if breakdown:
        breakdown_text = json.dumps(breakdown, indent=2)
        typed_text = ""
        for char in breakdown_text:
            typed_text += char
            placeholder.markdown(f"<div class='message agent'>{typed_text}</div>", unsafe_allow_html=True)
            time.sleep(0.002)

        # --- Generate Full Webpage Code ---
        generated_files = coder.implement(breakdown, plan)
        for f in generated_files:
            content_text = f"📄 {f['filename']}\n{f['content']}"
            typed_text = ""
            for char in content_text:
                typed_text += char
                placeholder.markdown(f"<div class='message agent' style='white-space: pre-wrap;'>{typed_text}</div>", unsafe_allow_html=True)
                time.sleep(0.002)

        # Optional: Download all files as zip
        import io, zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for f in generated_files:
                zf.writestr(f['filename'], f['content'])
        st.download_button("📥 Download All Files", zip_buffer.getvalue(), "project.zip")

    display_chat()
