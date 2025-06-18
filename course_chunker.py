import os
import json
from pathlib import Path
from nltk.tokenize import sent_tokenize

try:
    import tiktoken
except ImportError:
    tiktoken = None
    print("⚠️  tiktoken not installed, falling back to word count.")

def build_post_urls(filename):
    """
    Build 2 URLs per file.
    """
    url1 = f"https://tds.s-anand.net/#/{filename}"
    url2 = f"https://tds.s-anand.net/#/../{filename}"
    return [url1, url2]

def num_tokens(text, model_name="gpt-4o"):
    """
    Count tokens using tiktoken if available, else approximate by word count.
    """
    if tiktoken:
        enc = tiktoken.encoding_for_model(model_name)
        return len(enc.encode(text))
    else:
        return len(text.split())

def split_sentences(text):
    """
    Use nltk to split into sentences.
    """
    return sent_tokenize(text)

def smart_chunks(sentences, token_limit=4096, overlap_sentences=2):
    """
    Combine sentences into chunks <= token_limit tokens.
    Overlap few sentences for context.
    """
    chunks = []
    current = []
    current_tokens = 0

    for s in sentences:
        s_tokens = num_tokens(s)
        if current_tokens + s_tokens > token_limit and current:
            # Save current
            chunks.append(" ".join(current))
            # Overlap last few
            current = current[-overlap_sentences:] if overlap_sentences else []
            current_tokens = sum(num_tokens(x) for x in current)

        current.append(s)
        current_tokens += s_tokens

    if current:
        chunks.append(" ".join(current))

    return chunks

def process_course_file(md_file, output_dir, token_limit=4096):
    """
    Process a single .md file in the course dir.
    """
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read().strip()

    filename = md_file.name
    urls = build_post_urls(filename)

    sentences = split_sentences(content)
    chunks = smart_chunks(sentences, token_limit=token_limit)

    chunk_jsons = []
    for i, chunk in enumerate(chunks):
        chunk_data = {
            "id": f"{filename}#{i}",
            "post_urls": urls,
            "content": chunk.strip()
        }

        # Save each chunk as JSON file
        chunk_file = output_dir / f"{chunk_data['id']}.json"
        chunk_file.parent.mkdir(parents=True, exist_ok=True)
        with open(chunk_file, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)

        chunk_jsons.append(chunk_data)

    return chunk_jsons

def main():
    import nltk
    nltk.download('punkt')  # ensure sentence tokenizer is available

    course_root = Path("./course")
    chunks_root = Path("./chunks")
    chunks_root.mkdir(parents=True, exist_ok=True)

    all_chunks = []

    md_files = sorted([f for f in course_root.glob("*.md") if f.is_file() and f.suffix == ".md"])

    for md_file in md_files:
        chunk_jsons = process_course_file(md_file, chunks_root)
        all_chunks.extend(chunk_jsons)

    # Optionally save a combined all-in-one JSON too
    with open(chunks_root / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ Done! {len(all_chunks)} chunks saved individually in: {chunks_root}")

if __name__ == "__main__":
    main()
