import os
import pickle
import pdfplumber
from PIL import Image
import pytesseract
import openai
from llama_index.core.schema import TextNode
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# --- Load API key ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# --- Custom Embedding ---
class CustomEmbedding(BaseEmbedding):
    def _get_query_embedding(self, query: str) -> list[float]:
        return [0.0] * 512
    async def _aget_query_embedding(self, query: str) -> list[float]:
        return [0.0] * 512
    def _get_text_embedding(self, text: str) -> list[float]:
        return [0.0] * 512

# --- Load documents ---
def load_documents():
    folder = "Sanjukta"
    if os.path.exists(folder):
        return SimpleDirectoryReader(folder).load_data()
    return []

# --- Create/load index ---
def create_or_load_index():
    index_file = "index.pkl"
    if os.path.exists(index_file):
        with open(index_file, "rb") as f:
            return pickle.load(f)
    docs = load_documents()
    index = VectorStoreIndex(docs, embed_model=CustomEmbedding())
    with open(index_file, "wb") as f:
        pickle.dump(index, f)
    return index

# --- Query OpenAI ---
def query_openai_api(prompt: str):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        if "RateLimit" in str(e):
            return "⚛ API rate limit reached. Try again later."
        return f"⚛ Unexpected error: {str(e)}"

# --- Summarize previous messages ---
def summarize_messages(messages):
    text = "\n".join([f"{msg['role']}: {msg['message']}" for msg in messages])
    return query_openai_api(f"Summarize concisely:\n{text}\nSummary:")

# --- RAG retrieval stub ---
def rag_retrieve(query: str) -> list[str]:
    return []

# --- Chat agent ---
def chat_with_agent(query, index, chat_history, memory_limit=12, extra_file_content=""):
    retriever: BaseRetriever = index.as_retriever()
    nodes = retriever.retrieve(query)
    context = " ".join([node.get_text() for node in nodes if isinstance(node, TextNode)])
    if extra_file_content:
        context += f"\nAdditional context:\n{extra_file_content}"

    rag_context = "\n".join(rag_retrieve(query))
    full_context = context + "\n" + rag_context if rag_context else context

    if len(chat_history) > memory_limit:
        old_msgs = chat_history[:-memory_limit]
        recent_msgs = chat_history[-memory_limit:]
        summary = summarize_messages(old_msgs)
        conversation_text = f"Summary of previous conversation: {summary}\n"
    else:
        recent_msgs = chat_history
        conversation_text = ""

    for msg in recent_msgs:
        role_emoji = "⚛" if msg['role'] == "Agent" else "🧑‍🔬"
        conversation_text += f"{role_emoji}: {msg['message']}\n"
    conversation_text += f"🧑‍🔬: {query}\n"

    prompt = (
        f"Context: {full_context}\n"
        f"Conversation so far:\n{conversation_text}\n"
        "Instructions for AI:\n"
        "1. Understand the query fully.\n"
        "2. Automatically decide response depth:\n"
        "   - Short/factual → concise answer.\n"
        "   - Conceptual/technical/code → detailed structured answer.\n"
        "3. Include headings, examples, explanations if relevant.\n"
        "4. Provide full working code if programming question.\n"
        "5. Only answer the last user query.\n"
    )
    return query_openai_api(prompt)

# --- PDF text extraction ---
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

# --- Image OCR ---
def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image).strip()
