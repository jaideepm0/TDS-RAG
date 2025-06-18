# /// script
# requires-python = '>=3.13'
# dependencies = [
#     'fastapi',
#     'openai',
#     'python-dotenv',
#     'pydantic',
#     'numpy',
#     'scikit-learn',
#     'uvicorn',
# ]
# ///

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

load_dotenv()

# === API key ===
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

# === Config ===
EMBEDDINGS_PATH = "embeddings.npz"
TOP_K = 5  # how many relevant chunks to retrieve
SYSTEM_PROMPT = (
        "You are an virtual assistant for course Tools in Data Science."
        "Need to respond to user questions based on provided context."
        "Use the context to answer the question as accurately as possible."
        "If the context does not contain enough information, say 'I don't know'."
        "Generate a concise, clear answer in Markdown format."
        )
USER_PROMPT_TEMPLATE = """Context:
{context}

Question:
{question}
"""

# === FastAPI init ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Load embeddings and content ===
data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
texts = data['text_content']  # np.array of str
urls = data['urls']           # np.array of str
embeddings = data['embeddings']

# if len(texts) != len(urls) or len(urls) != len(embeddings):
#     raise ValueError("Mismatch: text_content, urls, and embeddings must have the same length.")

# === Request schema ===
class QueryRequest(BaseModel):
    question: str
    image: str | None = None  # base64 (data URL)


# === Image description helper ===
def describe_image(image_data: str) -> str:
    """
    Given a base64 data URL, get image description via LLM.
    """
    system_prompt = (
        "You are a precise assistant. "
        "Look at the image and write a clear, factual, concise Markdown description. "
        "Do NOT hallucinate. No extra text."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in Markdown:"},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            }
        ]
    )
    return response.choices[0].message.content.strip()


# === Embed query ===
def embed_query(text: str) -> np.ndarray:
    embedding = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return np.array(embedding.data[0].embedding).reshape(1, -1)


def retrieve_top_k(question: str, k: int) -> List[Tuple[str, str]]:
    """
    Returns list of (text, url) tuples for top-k chunks.
    """
    query_embedding = embed_query(question)
    scores = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:k]
    return [(texts[i], urls[i]) for i in top_indices]


# === RAG Endpoint ===
@app.post('/api')
async def rag_api(request: QueryRequest):
    question = request.question
    image_data = request.image

    # If image, describe it and append to question
    if image_data:
        try:
            image_description = describe_image(image_data)
            question = f"{question}\nImage Description:\n{image_description}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image description failed: {e}")

    # Retrieve top-K (text + url pairs)
    try:
        top_chunks_with_urls = retrieve_top_k(question, TOP_K)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")

    # Extract just text parts for prompt
    top_texts = [t for t, _ in top_chunks_with_urls]

    prompt = USER_PROMPT_TEMPLATE.format(
        context="\n\n".join(top_texts),
        question=question
    )

    # Generate answer
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    # Format links for response
    links = [{"url": u, "text": t} for t, u in top_chunks_with_urls]

    return {
        "answer": answer,
        "links": links
    }


@app.get('/')
async def root():
    return {"message": "Welcome to the RAG API."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
