import os
import streamlit as st
import json
import urllib.parse

from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="Lovable AI Web Builder", page_icon="💖", layout="wide")

# Sidebar
with st.sidebar:
    st.header("About Lovable AI")
    st.write("Type your website requirement and Lovable AI will generate a fully functional website!")
    st.info("Example: 'Build a dark-themed portfolio website with contact form and animations.'")
    if st.button("Reset Conversation"):
        st.session_state.messages = []

st.title("💖 Lovable AI Web Builder")

if "messages" not in st.session_state:
    st.session_state.messages = []

project_prompt = st.chat_input("Describe your website requirement:")

def save_generated_files(files, project_name):
    os.makedirs(project_name, exist_ok=True)
    for f in files:
        with open(os.path.join(project_name, f['filename']), 'w', encoding='utf-8') as fp:
            fp.write(f['content'])
    return os.path.abspath(project_name)

if project_prompt:
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

            # Save generated website
            project_folder = save_generated_files(generated_files, "lovable_ai_site")
            st.success(f"✅ Website generated at {project_folder}")

            # Create clickable link to open website
            index_file = os.path.join(project_folder, "index.html")
            st.markdown(
                f"🌐 [Click here to open your website](file://{index_file})",
                unsafe_allow_html=True
            )

            # Optional: download all files as zip
            import io, zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in generated_files:
                    zf.writestr(f['filename'], f['content'])
            st.download_button("📥 Download All Files", zip_buffer.getvalue(), "project.zip")
