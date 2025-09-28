import os
import streamlit as st
import json
import urllib.parse

from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="Coder Buddy", page_icon="⚡", layout="wide")

with st.sidebar:
    st.header("About Coder Buddy")
    st.write(
        "Automate AI project generation 🚀\n\n"
        "Type a request and let our multi-agent system plan, architect, and code your app!"
    )
    st.info("For best results, be specific: 'Build a PDF Q&A webapp using LlamaIndex.'")
    if st.button("Reset Conversation"):
        st.session_state.messages = []

st.title("🤖 Coder Buddy - AI Project Generator")
st.caption("Instant AI project generation, with conversational memory and full download.")

# Initialize chat message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the chat history using chat bubbles
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "project_plan" in message:
            st.markdown(f"**Project Plan:**\n{message['project_plan']}")
        elif "file_breakdown" in message:
            st.markdown(f"**File Breakdown:**")
            st.code(message["file_breakdown"], language="json")
        elif "files" in message:
            for f in message["files"]:
                with st.expander(f"📄 {f['filename']}"):
                    st.code(f['content'], language=f['filename'].split('.')[-1])
        else:
            st.markdown(message["content"])

project_prompt = st.chat_input(
    "Describe your AI project (e.g.: Build a PDF Q&A webapp using LlamaIndex)"
)

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please set in Streamlit Secrets.")
elif project_prompt:
    # Add user input to conversation
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
            with st.spinner("📄 Generating full code..."):
                generated_files = coder.implement(breakdown_dict, plan)
            st.session_state.messages.append({"role": "assistant", "files": generated_files})
            st.success("✅ Project created!")
            for f in generated_files:
                with st.expander(f"📄 {f['filename']}"):
                    st.code(f['content'], language=f['filename'].split('.')[-1])

            # Download as zip
            import io, zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in generated_files:
                    zf.writestr(f['filename'], f['content'])
            st.download_button(
                "📥 Download All Files", zip_buffer.getvalue(), "project.zip"
            )

            # New: Show clickable link to explore project idea on Google
            search_query = urllib.parse.quote(project_prompt)
            search_url = f"https://www.google.com/search?q={search_query}"
            st.markdown(f"### 🔗 Explore your project idea further: [Click here to search Google]({search_url})", unsafe_allow_html=True)

    st.balloons()
