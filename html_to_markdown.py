import glob
import json
import os
from pathlib import Path

from converter import convert

# === Config ===
project_root = Path("~/Programs/TDS/Project-1").expanduser()

base_url = 'https://discourse.onlinedegree.iitm.ac.in'

# === Find all ID dirs ===
id_dirs = glob.glob(f"{project_root}/content/posts/*/[0-9]*")

"""Give me the code block to add all the markdowns in the directory ./markdowns instead of the posts directory use os.makedirs"""


for id_dir in id_dirs:
    id_path = Path(id_dir)

    # Extract the thread name relative to posts directory
    # For example: if id_dir = .../content/posts/my-thread/123
    # then thread_name = my-thread
    thread_name = id_path.parent.name

    # Create target markdown directory:
    # ./markdowns/<thread_name>/<ID>
    target_dir = project_root / "markdowns" / thread_name / id_path.name
    os.makedirs(target_dir, exist_ok=True)

    # Find numbered JSON files only (skip posts.json)
    numbered_jsons = [
        p for p in id_path.glob("*.json") if p.name != "posts.json"
    ]

    for json_file in numbered_jsons:
        with open(json_file) as f:
            data = json.load(f)

        cooked_html = data.get("cooked", "")
        if not cooked_html:
            continue

        # Define the new .md path inside ./markdowns
        md_file = target_dir / json_file.with_suffix(".md").name

        print(f"Converting: {json_file} -> {md_file}")

        # === CONVERT ===
        markdown_content = convert(cooked_html)

        # --- META data
        metadata = {
            "post_url": base_url + data.get('post_url'),
            "reply_to_post_number": data.get('reply_to_post_number', None),
        }
        metadata = {k: str(v) for k, v in metadata.items() if v is not None}

        front_matter = "---\n" + '\n'.join(f"{k}: {v}" for k, v in metadata.items()) + "\n---\n"

        markdown_content = front_matter + markdown_content

        # === WRITE ===
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
