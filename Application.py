import streamlit as st
from Train import load_documents, create_or_load_index, chat_with_agent, extract_text_from_pdf
import time
import pdfplumber

st.set_page_config(page_title="BiswaLLM", page_icon="⚛", layout="wide")

# --- Initialize sessions ---
if 'index' not in st.session_state: st.session_state.index = create_or_load_index()
if 'sessions' not in st.session_state: st.session_state.sessions = []
if 'current_session' not in st.session_state: st.session_state.current_session = []

# --- Sidebar ---
st.sidebar.title("B͎i͎s͎w͎a͎L͎L͎M͎⚛")
if st.sidebar.button("New Chat"): st.session_state.current_session = []
if st.sidebar.button("Clear Chat"): st.session_state.current_session = []

for i, sess in enumerate(st.session_state.sessions):
    if st.sidebar.button(f"Session {i+1}"):
        st.session_state.current_session = sess.copy()

uploaded_file = st.sidebar.file_uploader("", type=["pdf"])
if uploaded_file and "uploaded_pdf_text" not in st.session_state:
    st.session_state.uploaded_pdf_text = extract_text_from_pdf(uploaded_file)

# --- Add message ---
def add_message(role, message):
    st.session_state.current_session.append({"role": role, "message": message})

# --- Custom responses ---
CUSTOM_RESPONSES = {
    "who created you": "I was created by Biswajit Mohapatra 🚀",
    "creator": "My creator is Biswajit Mohapatra.",
    "who is your father": "My father is Biswajit Mohapatra 👨‍💻",
    "father": "My father is Biswajit Mohapatra.",
    "who trained you": "I was trained by Biswajit Mohapatra.",
    "trained": "I was trained and fine-tuned by Biswajit Mohapatra."
}
def check_custom_response(user_input: str):
    normalized = user_input.lower()
    for keyword, response in CUSTOM_RESPONSES.items():
        if keyword in normalized: return response
    return None

# --- Display previous messages ---
for msg in st.session_state.current_session:
    align = "left" if msg['role']=="Agent" else "right"
    icon = "⚛" if msg['role']=="Agent" else "🧑‍🔬"
    st.markdown(f"<div style='text-align:{align};'>{icon} <b>{msg['message']}</b></div>", unsafe_allow_html=True)

# --- Header ---
if 'header_rendered' not in st.session_state:
    st.markdown("<h2 style='text-align:center; color:#b0b0b0;'>What can I help with? 😊</h2>", unsafe_allow_html=True)
    st.session_state.header_rendered = True

# --- Chat input ---
prompt = st.chat_input("Say something...", key="main_chat_input")
if prompt:
    add_message("User", prompt)
    st.markdown(f"<div style='text-align:right;'>🧑‍🔬 <b>{prompt}</b></div>", unsafe_allow_html=True)

    placeholder = st.empty()
    typed_text = ""

    if ("pdf" in prompt.lower() or "document" in prompt.lower()) and "uploaded_pdf_text" in st.session_state:
        if st.session_state.uploaded_pdf_text:
            final_answer = chat_with_agent(
                f"Please summarize this document:\n{st.session_state.uploaded_pdf_text}",
                st.session_state.index,
                st.session_state.current_session
            )
        else:
            final_answer = "⚛ Sorry, no readable text found in your PDF."
    else:
        final_answer = check_custom_response(prompt) or chat_with_agent(
            prompt, st.session_state.index, st.session_state.current_session
        )

    for char in final_answer:
        typed_text += char
        placeholder.markdown(f"<div style='text-align:left;'>⚛ <b>{typed_text}</b></div>", unsafe_allow_html=True)
        time.sleep(0.002)

    add_message("Agent", final_answer)

# --- Save session ---
if st.sidebar.button("Save Session"):
    if st.session_state.current_session not in st.session_state.sessions:
        st.session_state.sessions.append(st.session_state.current_session.copy())
