import re

# === EXAMPLE INPUT ===
text = """
Here is an image:
[![Screenshot 2025-02-05 182750](https://europe1.discourse-cdn.com/flex013/uploads/iitm/optimized/3X/d/7/d7e9677b9a8d204c98e6008ef57a884177301fad_2_690x366.png)

Screenshot 2025-02-05 1827501917×1018 38.3 KB](https://europe1.discourse-cdn.com/flex013/uploads/iitm/original/3X/d/7/d7e9677b9a8d204c98e6008ef57a884177301fad.png "Screenshot 2025-02-05 182750")

Here is a normal Markdown image:
![Alt Text](https://example.com/image.png)
"""

def extract_and_replace_images(text: str) -> str:
    """
    Find markdown image links in text:
    - [![alt](preview)...](original) --> keep only preview URL
    - ![alt](url) --> keep only URL

    Any caption, whitespace, or newlines between parts is ignored.
    """

    pattern = re.compile(
        r"""
        \[                     # opening [
          !\[.*?\]             # inner image ![alt]
          \(
            (?P<preview>[^)]+) # preview URL
          \)
          .*?                  # caption or whitespace (can include newlines)
        \]
        \(
          [^)\s]+              # original URL (ignored)
          [^)]* 
        \)
        |
        !\[.*?\]               # normal markdown image ![alt]
        \(
          (?P<normal>[^)]+)    # normal URL
        \)
        """,
        re.VERBOSE | re.DOTALL
    )

    def replacer(match: re.Match) -> str:
        """
        Replace match with the extracted preview or normal URL.
        """
        url = match.group('preview') or match.group('normal')
        return url.strip()

    return pattern.sub(replacer, text)

# === APPLY ===

print(extract_and_replace_images(text))
