
from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load backend/.env regardless of the terminal's working directory
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE, override=True)


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to backend/.env."
        )

    return genai.Client(api_key=api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = get_client()

    model = os.getenv(
        "GEMINI_EMBEDDING_MODEL",
        "gemini-embedding-001"
    )

    response = client.models.embed_content(
        model=model,
        contents=texts
    )

    if not response.embeddings:
        raise RuntimeError("Gemini returned no embeddings.")

    return [embedding.values for embedding in response.embeddings]


def generate_answer(question: str, contexts: list[dict]) -> str:
    client = get_client()

    model = os.getenv(
        "GEMINI_CHAT_MODEL",
        "gemini-2.5-flash"
    )

    context_text = "\n\n".join(
        f"[Source item {c['item_id']}, chunk {c['chunk_id']}] "
        f"{c['content']}"
        for c in contexts
    )

    system_instruction = (
        "Answer the user's question using only the supplied context. "
        "If the context does not contain the answer, say you do not have "
        "enough information. Cite supporting sources inline using "
        "[item ID]. Do not invent citations."
    )

    response = client.models.generate_content(
        model=model,
        contents=(
            f"Context:\n{context_text}\n\n"
            f"Question: {question}"
        ),
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
        ),
    )

    return response.text or "I could not generate an answer."
