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

# --- Load API key from environment ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# --- Custom Embedding class (stub) ---
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
    else:
        print(f"⚠️ Folder '{folder}' not found. Continuing with empty documents.")
        return []

# --- Create or load index ---
def create_or_load_index():
    index_file = "index.pkl"
    if os.path.exists(index_file):
        with open(index_file, "rb") as f:
            index = pickle.load(f)
    else:
        docs = load_documents()
        embedding_model = CustomEmbedding()
        index = VectorStoreIndex(docs, embed_model=embedding_model)
        with open(index_file, "wb") as f:
            pickle.dump(index, f)
    return index

# --- Query OpenAI API (1.0+ syntax) ---
def query_openai_api(prompt: str):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        err_msg = str(e)
        if "RateLimit" in err_msg:
            return "⚛ Sorry, the API rate limit has been reached. Please try again later."
        return f"⚛ An unexpected error occurred: {err_msg}"

# --- Summarize previous messages ---
def summarize_messages(messages):
    text = ""
    for msg in messages:
        text += f"{msg['role']}: {msg['message']}\n"
    prompt = f"Summarize the following conversation concisely:\n{text}\nSummary:"
    return query_openai_api(prompt)

# --- Stub RAG retrieval ---
def rag_retrieve(query: str) -> list[str]:
    return []
def chat_with_agent(query, index, chat_history, memory_limit=12, extra_file_content=""):
    retriever: BaseRetriever = index.as_retriever()
    nodes = retriever.retrieve(query)
    context = " ".join([node.get_text() for node in nodes if isinstance(node, TextNode)])

    if extra_file_content:
        context += f"\nAdditional context from uploaded file:\n{extra_file_content}"

    rag_results = rag_retrieve(query)
    rag_context = "\n".join(rag_results)
    full_context = context + "\n" + rag_context if rag_context else context

    if len(chat_history) > memory_limit:
        old_messages = chat_history[:-memory_limit]
        recent_messages = chat_history[-memory_limit:]
        summary = summarize_messages(old_messages)
        conversation_text = f"Summary of previous conversation: {summary}\n"
    else:
        recent_messages = chat_history
        conversation_text = ""

    for msg in recent_messages:
        conversation_text += f"{msg['role']}: {msg['message']}\n"
    conversation_text += f"User: {query}\n"

    # --- Adaptive response instruction ---
    # Ask the model to generate responses based on query complexity
    prompt = (
        f"Context from documents and files: {full_context}\n"
        f"Conversation so far:\n{conversation_text}\n"
        "Instruction for AI: Analyze the user's query carefully. "
        "If it is asking for a factual answer or abbreviation, give a short and precise response. "
        "If it is asking for an explanation, concept, or technical topic, give a detailed, structured, and clear answer "
        "with headings, subheadings, examples, and context when necessary. "
        "Always prioritize relevance and clarity over length. "
        "Provide the best possible answer for the user's query."
    )

    return query_openai_api(prompt)


# --- PDF text extraction ---
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

# --- Image OCR extraction ---
def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

