import os
import streamlit as st
import json
from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="Coder Buddy", page_icon="⚡", layout="wide")
st.title("🤖 Coder Buddy - AI Project Generator")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please set it in Streamlit Secrets.")
else:
    user_request = st.text_area("Enter your project request", "Create a to-do list app using HTML, CSS, and JavaScript")

    if st.button("Generate Project"):
        planner = PlannerAgent(api_key)
        architect = ArchitectAgent(api_key)
        coder = CoderAgent(api_key)

        with st.spinner("📌 Generating project plan..."):
            plan = planner.plan(user_request)
        st.subheader("📋 Project Plan")
        st.write(plan)

        with st.spinner("📌 Breaking down into files..."):
            try:
                breakdown = architect.design(plan)
                st.subheader("📂 File Breakdown")
                st.code(json.dumps(breakdown, indent=2), language="json")
            except ValueError as e:
                st.error(f"❌ Architect output is not valid JSON: {e}")
                breakdown = []

        if breakdown:
            with st.spinner("📌 Generating full webpage code..."):
                generated_files = coder.implement(breakdown, plan)

            st.success("✅ Project created successfully!")
            for f in generated_files:
                st.subheader(f"📄 {f['filename']}")
                st.code(f['content'], language=f['filename'].split('.')[-1])

            # Optional: allow user to download as zip
            import io, zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in generated_files:
                    zf.writestr(f['filename'], f['content'])
            st.download_button("📥 Download All Files", zip_buffer.getvalue(), "project.zip")
