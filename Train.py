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

def converse_with_ai(query, index, chat_history, memory_limit=12, extra_file_content=""):
    retriever: BaseRetriever = index.as_retriever()
    nodes = retriever.retrieve(query)
    context_text = " ".join([node.get_text() for node in nodes if isinstance(node, TextNode)])

    if extra_file_content:
        context_text += f"\nAdditional context from uploaded file:\n{extra_file_content}"

    rag_results = rag_retrieve(query)
    rag_text = "\n".join(rag_results)
    full_context = context_text + "\n" + rag_text if rag_text else context_text

    if len(chat_history) > memory_limit:
        old_msgs = chat_history[:-memory_limit]
        recent_msgs = chat_history[-memory_limit:]
        summary_text = summarize_messages(old_msgs)
        conversation_history = f"Summary of previous conversation: {summary_text}\n"
    else:
        recent_msgs = chat_history
        conversation_history = ""

    for msg in recent_msgs:
        conversation_history += f"{msg['message']}\n"

    conversation_history += f"{query}\n"

    prompt_text = (
        f"Context from documents and files: {full_context}\n"
        f"Conversation so far:\n{conversation_history}\n"
        "Instructions for AI:\n"
        "1. Respond only once using ⚛ emoji.\n"
        "2. Do NOT include user emojis or repeat user text.\n"
        "3. Short/factual queries → concise answers.\n"
        "4. Conceptual/technical/code queries → structured answers with headings, bullets, examples, full working code if applicable.\n"
        "5. Avoid repeating prefixes or unnecessary text.\n"
        "6. Only answer the last user query.\n"
    )

    answer = query_openai_api(prompt_text)
    return f"⚛ {answer.strip()}"



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



