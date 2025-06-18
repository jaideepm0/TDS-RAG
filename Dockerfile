FROM python:3.13-slim

# Install uv
RUN pip install uv \
    uvicorn \
    fastapi \
    numpy \
    scikit-learn \
    python-dotenv \
    openai \
    pydantic

WORKDIR /app

# Copy only what's needed
COPY app.py /app/
COPY embeddings.npz /app/
COPY .env /app/


ENV UV_CACHE_DIR=/app/.cache/uv

# Port for HF Spaces
EXPOSE 7860

# Run with uv + uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
