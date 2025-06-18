# ///// script
# requires-python = '>=3.13'
# dependencies = [
#     'fastapi',
#     'openai',
#     'python-dotenv',
#     'pydantic',
#     'chromadb',
#     'lancedb',
#     'duckdb',
# ]
# ///

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Config ===
EMBEDDINGS_PATH = "embeddings.npz"
TOP_K = 3  # number of chunks to retrieve
SYSTEM_PROMPT = "You are a helpful assistant using retrieved context to answer the question."
USER_PROMPT_TEMPLATE = """Context:
{context}

Question:
{question}
"""

# Initialize
app = FastAPI()
client = OpenAI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embeddings and chunks
data = np.load(EMBEDDINGS_PATH, allow_pickle=True)
chunks = data['chunks']   # list of strings
embeddings = data['embeddings']  # numpy array

if len(chunks) != len(embeddings):
    raise ValueError("Mismatch between number of chunks and embeddings.")

# === Request Schema ===
class QueryRequest(BaseModel):
    question: str
    image: str = None  # optional, you can pass base64


# === Helper: Embed query ===
def embed_query(text: str) -> np.ndarray:
    # For real usage, replace with your own embedding model if needed
    embedding = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return np.array(embedding.data[0].embedding).reshape(1, -1)


# === Helper: Retrieve top-k ===
def retrieve_top_k(question: str, k: int) -> List[str]:
    query_embedding = embed_query(question)
    scores = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:k]
    return [chunks[i] for i in top_indices]


# === Endpoint ===
@app.post("/api")
async def rag_api(request: QueryRequest):
    question = request.question
    image_data = request.image  # not used here, just passed along if needed

    try:
        top_chunks = retrieve_top_k(question, TOP_K)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    prompt = USER_PROMPT_TEMPLATE.format(
        context="\n\n".join(top_chunks),
        question=question
    )

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
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "answer": answer,
        "top_chunks": top_chunks
    }
