import re

from bs4 import BeautifulSoup
from markdownify import markdownify
from image import describe_image

"""
Import anther script ./image.py to get the image description function.
Refactor the output from text.strip() to update the Image description.
Cache the Image description so no need to call the LLM again.
Regex -> find the image in the markdown text and replace it with the cached description.
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
        description = describe_image(url.strip())
        return description

    return pattern.sub(replacer, text)



def convert(html):

    text = markdownify(html)
    return extract_and_replace_images(text.strip())
