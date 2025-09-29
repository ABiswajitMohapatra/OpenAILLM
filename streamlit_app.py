import os
import streamlit as st
import json
import urllib.parse
import threading
import http.server
import socketserver
import webbrowser
import io
import zipfile

from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

# Get API key from secrets or environment
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
project_prompt = st.chat_input("Describe your website or app requirement:")

# ----------------- Helper functions -----------------
def save_generated_files(files, project_name):
    os.makedirs(project_name, exist_ok=True)
    for f in files:
        with open(os.path.join(project_name, f['filename']), 'w', encoding='utf-8') as fp:
            fp.write(f['content'])
    return os.path.abspath(project_name)

def serve_website(folder_path, port=8000):
    os.chdir(folder_path)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    threading.Thread(target=lambda: webbrowser.open(f"http://localhost:{port}")).start()
    httpd.serve_forever()

# ----------------- Main logic -----------------
if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please set in Streamlit Secrets.")
elif project_prompt:
    st.session_state.messages.append({"role": "user", "content": project_prompt})

    planner = PlannerAgent(api_key)
    architect = ArchitectAgent(api_key)
    coder = CoderAgent(api_key)

    with st.chat_message("assistant"):
        # Generate project plan
        with st.spinner("📌 Generating project plan..."):
            plan = planner.plan(project_prompt)
        st.session_state.messages.append({"role": "assistant", "project_plan": plan})
        st.markdown(f"**Project Plan:**\n{plan}")

        # Generate file breakdown
        with st.spinner("📂 Breaking down into files..."):
            try:
                breakdown_dict = architect.design(plan)
                breakdown_str = json.dumps(breakdown_dict, indent=2)
                st.session_state.messages.append({"role": "assistant", "file_breakdown": breakdown_str})
                st.markdown("**File Breakdown:**")
                st.code(breakdown_str, language="json")
            except ValueError as e:
                st.error(f"❌ Architect output is not valid JSON: {e}")
                breakdown_dict = []

        # Generate each file
        if breakdown_dict:
            generated_files = []
            with st.spinner("📄 Generating files one by one..."):
                for part in breakdown_dict:
                    file = coder.implement([part], plan)[0]
                    generated_files.append(file)
                    st.session_state.messages.append({"role": "assistant", "files": [file]})
                    with st.expander(f"📄 {file['filename']}"):
                        st.code(file['content'], language=file['filename'].split('.')[-1])

            # Save files and serve website
            project_folder = save_generated_files(generated_files, "coder_buddy_site")
            st.success(f"✅ Website generated at {project_folder}")

            threading.Thread(target=lambda: serve_website(project_folder)).start()
            st.info("🌐 Your website is being opened in a new browser tab!")

            # Download zip of all files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in generated_files:
                    zf.writestr(f['filename'], f['content'])
            st.download_button("📥 Download All Files", zip_buffer.getvalue(), "project.zip")

            # Balloons for celebration
            st.balloons()
