import numpy as np
from urllib.parse import urlparse
from pathlib import Path

# === Load ===
EMBEDDINGS_FILE = "embeddings.npz"
data = np.load(EMBEDDINGS_FILE, allow_pickle=True)

text_content = data["text_content"]
urls_list = data["urls"]
embeddings = data["embeddings"]

# === Update URLs ===
updated_urls = []

for urls in urls_list:
    # Make sure it's a list
    if isinstance(urls, np.ndarray):
        urls = urls.tolist()
    if not urls:
        updated_urls.append([])
        continue

    # Extract slug and id from any URL (they all belong to the same thread)
    # Example: https://discourse.../slug/id/num
    sample = urls[0]
    parsed = urlparse(sample)
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 4:
        slug = parts[1]
        thread_id = parts[2]
        thread_slug_id = f"{slug}/{thread_id}"
    else:
        # fallback: root only
        thread_slug_id = "unknown"

    # Use a set to ensure uniqueness
    unique_urls = set(urls)
    unique_urls.add(thread_slug_id)

    updated_urls.append(sorted(unique_urls))

# === Save updated ===
np.savez_compressed(
    "embeddings.npz",
    text_content=text_content,
    urls=np.array(updated_urls, dtype=object),
    embeddings=embeddings
)

print(f"✅ Updated file saved as embeddings.npz")
