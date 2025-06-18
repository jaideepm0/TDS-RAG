
import os

import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    """
    Get the embedding for a given text using OpenAI's API.

    Args:
        text (str): The text to embed.
        model (str): The model to use for embedding. Default is "text-embedding-3-small".

    Returns:
        list: The embedding vector for the text.
    """
    openai.api_key = OPENAI_API_KEY
    response = openai.Embedding.create(input=text, model=model)
    return response['data'][0]['embedding']
