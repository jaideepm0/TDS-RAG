import os
import json
from pathlib import Path
from nltk.tokenize import sent_tokenize

try:
    import tiktoken
except ImportError:
    tiktoken = None
    print("⚠️  tiktoken not installed, falling back to word count.")

def parse_md_file(path):
    """
    Extract post_url and content.
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    post_url = ""
    content = []
    in_front = False
    for line in lines:
        if line.strip() == "---":
            if not in_front:
                in_front = True
            else:
                in_front = False
                continue
        elif in_front:
            if line.startswith("post_url:"):
                post_url = line.split(":", 1)[1].strip()
        else:
            content.append(line)

    return post_url, "".join(content).strip()


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


def process_topic(topic_dir, output_dir, token_limit=4096):
    """
    Process a topic_id folder: parse, split, chunk, and save JSON.
    """
    print(f"Processing topic: {topic_dir}")
    files = sorted(Path(topic_dir).glob("*.md"), key=lambda p: int(p.stem))
    all_sentences = []
    urls = []

    for file in files:
        url, content = parse_md_file(file)
        sentences = split_sentences(content)
        all_sentences.extend(sentences)
        urls.append(url)

    # Chunk
    chunks = smart_chunks(all_sentences, token_limit=token_limit)

    # Format: id, content, post_urls
    relative_topic = topic_dir.relative_to("markdowns")
    topic_name = str(relative_topic)
    output = []
    for i, chunk in enumerate(chunks):
        output.append({
            "id": f"{topic_name}#{i}",
            "post_urls": urls,
            "content": chunk.strip()
        })

    # Write JSON
    out_file = output_dir / relative_topic / "chunks.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved: {out_file} ({len(chunks)} chunks)")


def main():
    import nltk
    nltk.download('punkt')  # for sentence tokenizer

    markdown_root = Path("./markdowns")
    chunks_root = Path("./chunks")

    topic_dirs = [p for p in markdown_root.glob("*/*") if p.is_dir()]
    for topic_dir in topic_dirs:
        process_topic(topic_dir, chunks_root)


if __name__ == "__main__":
    main()
