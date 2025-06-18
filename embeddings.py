import os
import json
from pathlib import Path

import openai
import numpy as np
from dotenv import load_dotenv

# Load your .env OpenAI key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

client = openai.OpenAI()

# === Config ===
CHUNKS_DIR = Path("./chunks")  # adjust if needed
OUTPUT_FILE = "embeddings.npz"
EMBEDDING_MODEL = "text-embedding-3-large"


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> list:
    """
    Get the embedding for a given text using OpenAI's API.
    """
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding


def find_all_chunks_json(base_dir: Path):
    """
    Recursively find all chunks.json files under the given base directory.
    """
    return list(base_dir.rglob("chunks.json"))


def build_post_urls(file: Path, base_dir: Path):
    """
    Given the path to a chunks.json file, build a post URL:
    - For tree style: use parts between base_dir and chunks.json
    - For loose MD#0.json files: fallback to the filename stem
    """
    rel_parts = file.relative_to(base_dir).parts
    if len(rel_parts) > 1:
        # Typical: slug / id / chunks.json
        slug, id_ = rel_parts[0], rel_parts[1]
        thread_url = f"{slug}/{id_}"
    else:
        # Fallback: single file like actor-network-visualization.md#0.json
        thread_url = file.stem
    return thread_url


def main():
    chunk_files = find_all_chunks_json(CHUNKS_DIR)
    print(f"📂 Found {len(chunk_files)} chunk JSONs under {CHUNKS_DIR}")

    texts = []
    urls = []
    embeddings = []

    for file in chunk_files:
        with open(file, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)

        # Make robust: handle list or dict
        chunk_items = chunk_data if isinstance(chunk_data, list) else [chunk_data]

        # Build clean post URL (slug/id)
        post_url = build_post_urls(file, CHUNKS_DIR)

        for item in chunk_items:
            text = item["content"]
            post_urls = item.get("post_urls") or []  # fallback if not present

            emb = get_embedding(text)

            texts.append(text)
            urls.append(post_urls if post_urls else [post_url])  # use fallback if empty
            embeddings.append(emb)

            print(f"✅ Embedded: {file}  -> {post_url}")

    embeddings_np = np.array(embeddings, dtype=np.float32)

    np.savez_compressed(
        OUTPUT_FILE,
        text_content=np.array(texts, dtype=object),
        urls=np.array(urls, dtype=object),
        embeddings=embeddings_np
    )

    print(f"\n✅ Done! All embeddings saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

