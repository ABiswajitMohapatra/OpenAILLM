import os
import streamlit as st
import json
import threading
import http.server
import socketserver
import webbrowser
from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="💖 Lovable AI Web Builder", page_icon="💖", layout="wide")

with st.sidebar:
    st.header("About Lovable AI")
    st.write(
        "Type your website requirement and Lovable AI will generate a live, fully functional website!"
    )
    st.info("Example: 'Build a dark-themed portfolio website with contact form and animations.'")
    if st.button("Reset Conversation"):
        st.session_state.messages = []

st.title("💖 Lovable AI Web Builder")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
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

project_prompt = st.chat_input("Describe your website requirement:")

def save_generated_files(files, project_name="lovable_ai_site"):
    # Create proper folder structure
    os.makedirs(project_name, exist_ok=True)
    assets_folder = os.path.join(project_name, "assets")
    os.makedirs(assets_folder, exist_ok=True)

    for f in files:
        # CSS/JS goes into assets folder
        if f['filename'].endswith((".css", ".js")):
            file_path = os.path.join(assets_folder, f['filename'])
        else:
            file_path = os.path.join(project_name, f['filename'])

        with open(file_path, 'w', encoding='utf-8') as fp:
            fp.write(f['content'])
    return os.path.abspath(project_name)

def serve_website(folder_path, port=8000):
    os.chdir(folder_path)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    webbrowser.open(f"http://localhost:{port}/index.html")
    httpd.serve_forever()

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please set in Streamlit Secrets.")
elif project_prompt:
    st.session_state.messages.append({"role": "user", "content": project_prompt})

    planner = PlannerAgent(api_key)
    architect = ArchitectAgent(api_key)
    coder = CoderAgent(api_key)

    with st.chat_message("assistant"):
        with st.spinner("📌 Generating project plan..."):
            plan = planner.plan(project_prompt)
        st.session_state.messages.append({"role": "assistant", "project_plan": plan})
        st.markdown(f"**Project Plan:**\n{plan}")

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

        if breakdown_dict:
            generated_files = []
            with st.spinner("📄 Generating files one by one..."):
                for part in breakdown_dict:
                    file = coder.implement([part], plan)[0]
                    generated_files.append(file)
                    st.session_state.messages.append({"role": "assistant", "files": [file]})
                    with st.expander(f"📄 {file['filename']}"):
                        st.code(file['content'], language=file['filename'].split('.')[-1])

            # Save files to folder
            project_folder = save_generated_files(generated_files)
            st.success(f"✅ Website generated at {project_folder}")

            # Serve website live in a thread
            threading.Thread(target=lambda: serve_website(project_folder), daemon=True).start()
            st.info("🌐 Your website is being opened in a new browser tab!")

            # Optional: download zip
            import io, zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in generated_files:
                    zf.writestr(f['filename'], f['content'])
            st.download_button("📥 Download All Files", zip_buffer.getvalue(), "project.zip")
            st.balloons()
