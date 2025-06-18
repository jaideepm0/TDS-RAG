### NOTE:
**Every LLM request has been sent with my personal OpenAI key. 
I haven't used the keys provided by the TDS team. 
Not to waste their credits when I can just pay few dollars for my own**

### Building commands

```bash
uv run scrape.py
git clone --branch tds-2025-01 --single-branch https://github.com/sanand0/tools-in-data-science-public.git
uv run html_to_markdown.py
uv run chunker.py
uv run course_chunker.py
uv run embeddings.py
uv run update.py
uv run app.py
```

> Disclaimer:
- The errors might be thrown but that doesn't happen if you have the cached file directories in the repo.
- Every file is created programmatically so no need to worry about the files.
> Reason for errors:
- To know at what point something gone wrong. and cache them (so no errors were caught properly.)
- Re run as the failed part is cached no need to worry about it.

---

### Deploy commands

```bash
mkdir build
cd build
git clone git@hf.co:spaces/jaideepm0/TDS-RAG 
cd ..
cp app.py .env Dockerfile embeddings.npz ./build/TDS-RAG/
cd ./build/TDS-RAG

git lfs install
git lfs track embeddings.npz
git add .
git commit -m 'asdf'
git push origin main
```

---

**Discourse scraping file** -> `scrape.py`

### My Env Setup
```bash
sudo pacman -S git git-lfs python uv 
export OPENAI_API_KEY=my-personal-key >> ~/.zshrc
export OPENAI_API_KEY=my-personal-key >> ~/.bashrc
```
