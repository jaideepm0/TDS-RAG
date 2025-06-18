import base64
import os
import shutil
from pathlib import Path
import hashlib

import httpx
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI()

# Ensure temp directory exists
TEMP_DIR = Path('./temp')
TEMP_DIR.mkdir(exist_ok=True)
CACHE_DIR = Path('./image_description')
CACHE_DIR.mkdir(exist_ok=True)

FAILED_CACHE_FILE = CACHE_DIR / "failed.txt"

if FAILED_CACHE_FILE.exists():
    FAILED_HASHES = {
        line.split(None, 1)[0]  # only the hash part
        for line in FAILED_CACHE_FILE.read_text().splitlines()
    }
else:
    FAILED_HASHES = set()


SYSTEM_PROMPT = (
    "You are a highly precise assistant. "
    "You will look at an input image and generate a clear, concise, and informative description of it. "
    "Do NOT hallucinate. Write the description in clean Markdown, suitable for reading in a document. "
    "Do not add anything extra or repeat instructions."
)

def download_image(url, dest):
    """Download an image to the destination path."""
    hash_name = get_cache_filename(url).stem
    url = url.split()[0]

    with httpx.stream("GET", url) as r:
        if r.status_code != 200:
            with open(FAILED_CACHE_FILE, "a") as f:
                f.write(f"{hash_name} {url}\n")
            r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)

def image_to_base64(image_path):
    """Read an image and return base64 data URL."""
    ext = image_path.suffix.lstrip('.').lower()
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/{ext};base64,{encoded}"


def get_cache_filename(image_url):
    """Generate a safe filename for the cache, using a hash."""
    hash_name = hashlib.sha256(image_url.encode()).hexdigest()
    return CACHE_DIR / f"{hash_name}.md"

def describe_image(image_url):
    """Download, encode, send to LLM, clean up, return description."""


    if not image_url.startswith("https://europe1.discourse-cdn.com/") or image_url.endswith(".avif"):
        """this are the only images that are uploaded else are just profile images"""
        return ""


    hash_name = get_cache_filename(image_url).stem

    if hash_name in FAILED_HASHES:
        return ""

    # === Check cache ===
    cache_file = get_cache_filename(image_url)
    if cache_file.exists():
        return cache_file.read_text(encoding='utf-8').strip()

    # Download image to temp
    filename = TEMP_DIR / Path(image_url).name
    download_image(image_url, filename)

    # Encode to base64 data URL
    data_url = image_to_base64(filename)

    # Create request payload
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in Markdown:"},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ]
    )

    # Delete the image file after processing
    filename.unlink(missing_ok=True)

     # === Cache and return ===
    description = response.choices[0].message.content.strip()
    cache_file.write_text(description, encoding='utf-8')
    return description


if __name__ == "__main__":
    # EXAMPLE USAGE
    image_urls = [
            "https://europe1.discourse-cdn.com/flex013/uploads/iitm/original/3X/6/a/6a4a28aa638840e8d2e4dbf246ca235fd41e5ccb.png",
    ]

    for url in image_urls:
        description = describe_image(url)
        print(f"## Description for {url}:\n{description}\n")
