import os
import streamlit as st
import json
import urllib.parse
import io
import zipfile
import streamlit.components.v1 as components

from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

# Get API key from Streamlit Secrets or environment
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="Coder Buddy Live Web Builder", page_icon="⚡", layout="wide")

with st.sidebar:
    st.header("About Coder Buddy")
    st.write(
        "Type your website or app requirement and Coder Buddy will generate a live, fully functional website!"
    )
    st.info("Example: 'Build a dark-themed portfolio website with contact form and animations.'")
    if st.button("Reset Conversation"):
        st.session_state.messages = []

st.title("⚡ Coder Buddy - AI Live Web Builder")

# Initialize chat message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "project_plan" in message:
            st.markdown(f"**Project Plan:**\n{message['project_plan']}")
        elif "file_breakdown" in message:
            st.markdown("**File Breakdown:**")
            st.code(message["file_breakdown"], language="json")
        elif "files" in message:
            for f in message["files"]:
                with st.expander(f"📄 {f['filename']}"):
                    st.code(f['content'], language=f['filename'].split('.')[-1])
        else:
            st.markdown(message["content"])

# Chat input for project prompt
project_prompt = st.chat_input("Describe your website or app requirement
