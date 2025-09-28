import os
import streamlit as st
from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

# Get API key from Streamlit Cloud Secrets
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="Coder Buddy", page_icon="⚡", layout="wide")
st.title("🤖 Coder Buddy - AI Project Generator")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Please set it in Streamlit Cloud Secrets.")
else:
    user_request = st.text_area(
        "Enter your project request",
        "Create a to-do list app using HTML, CSS, and JavaScript"
    )

    if st.button("Generate Project"):
        planner = PlannerAgent(api_key)
        architect = ArchitectAgent(api_key)
        coder = CoderAgent(api_key)

        with st.spinner("📌 Generating project plan..."):
            plan = planner.plan(user_request)
        st.subheader("📋 Project Plan")
        st.write(plan)

        with st.spinner("📌 Breaking down into files..."):
            breakdown = architect.design(plan)
        st.subheader("📂 File Breakdown")
        st.code(breakdown, language="json")

        with st.spinner("📌 Writing code files..."):
            result = coder.implement(breakdown)
        st.success("✅ Project created successfully!")
        st.text(result)

