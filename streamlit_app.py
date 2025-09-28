import os
import streamlit as st
import json

from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="Coder Buddy", page_icon="⚡", layout="wide")

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/1/1b/CoderBuddy.png", 
        width=120
    )
    st.header("About Coder Buddy")
    st.write(
        "Automate AI project generation 🚀\n\n"
        "Type a request and let our multi-agent system plan, architect, and code your app!"
    )
    st.info(
        "For best results, be specific with your project request. Example: "
        "'Build a PDF Q&A webapp using LlamaIndex.'"
    )

st.title("🤖 Coder Buddy - AI Project Generator")
st.caption(
    "Instantly get a complete AI project (plan, file breakdown, code, and downloadable ZIP) with one click."
)

# Modern LLM-style prompt
project_prompt = st.chat_input(
    "Describe your AI project (e.g.: Build a PDF Q&A webapp using LlamaIndex)"
)

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please set it in Streamlit Secrets.")
elif project_prompt:
    user_request = project_prompt.strip()
    planner = PlannerAgent(api_key)
    architect = ArchitectAgent(api_key)
    coder = CoderAgent(api_key)

    with st.spinner("📌 Generating project plan..."):
        plan = planner.plan(user_request)
    st.success("📋 Project Plan")
    st.write(plan)

    with st.spinner("📂 Breaking down into files..."):
        try:
            breakdown = architect.design(plan)
            st.subheader("📂 File Breakdown")
            with st.expander("See file breakdown (JSON)", expanded=False):
                st.code(json.dumps(breakdown, indent=2), language="json")
        except ValueError as e:
            st.error(f"❌ Architect output is not valid JSON: {e}")
            breakdown = []

    if breakdown:
        with st.spinner("📄 Generating full webpage code..."):
            generated_files = coder.implement(breakdown, plan)
        st.success("✅ Project created successfully!")
        for f in generated_files:
            with st.expander(f"📄 {f['filename']}"):
                st.code(f['content'], language=f['filename'].split('.')[-1])

        # Download as zip (unchanged)
        import io, zipfile
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for f in generated_files:
                zf.writestr(f['filename'], f['content'])
        st.download_button(
            "📥 Download All Files", zip_buffer.getvalue(), "project.zip"
        )
