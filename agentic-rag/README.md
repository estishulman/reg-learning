# Agentic Coding Knowledge RAG

A three-stage learning project that unifies Markdown documentation from **Cursor**, **Claude Code** and **Kiro**.

## Features
- **Stage A:** Markdown ingestion, metadata, SentenceSplitter chunks, Cohere multilingual embeddings, Pinecone VectorStoreIndex, retriever, LlamaIndex response synthesizer and Gradio chat.
- **Stage B:** Typed events (`QueryEvent`, `RetrievedEvent`, `AnswerEvent`), state tracking, validation, score threshold and one retry when no confident results are found.
- **Stage C:** JSON extraction for decisions, rules and warnings, simple deterministic question routing, time filtering and evidence-grounded LLM answers.

## Setup (Python 3.10+)
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env  # Windows: copy .env.example .env
```
Fill `COHERE_API_KEY` and `PINECONE_API_KEY` in `.env`. Never commit this file.

## Run
```bash
agentic-rag index --root sample_project
agentic-rag extract --root sample_project
agentic-rag chat
pytest -q
```
For a real codebase set `PROJECT_ROOT` or pass `--root` to `index` and `extract`. Supported folders: `.cursor/**/*.md`, `.claude/**/*.md`, `.kiro/**/*.md`.

Pinecone index is auto-created in AWS us-east-1 at **dimension 1024** for Cohere multilingual v3. If the index already exists it must have dimension 1024. Indexing the same project repeatedly may create duplicate vectors; use a fresh namespace for each run or implement incremental upserts before production.

## Design decisions / limitations
- **Retrieval vs decisions:** Semantic retrieval supplies evidence; synthesis produces a grounded answer, not an autonomous code change.
- **Structured extraction baseline:** Stage C uses deterministic keyword extraction, not LLM structured prediction. It can miss paraphrases, misclassify items, and cannot infer superseded rules. This is an explicit partial implementation of Stage C.
- **Routing:** Simple keyword heuristic, not LlamaIndex Router. Expand with a router and schema-constrained LLM extraction for full assignment compliance.
- **Dates:** `observed_at` uses file modification time, not the historical decision date. Time-based questions are therefore approximate.
- **State:** Scoped to each query; events carry the current payload, state holds route and retry count. A step does not have to call an LLM.
- **Security:** Local files are treated as untrusted evidence, never executable instructions. Avoid uploading secrets to third-party AI services. The sample project contains synthetic data.
- **Networking:** Requires access to Cohere and Pinecone. Corporate/NetFree TLS environments may need administrator-approved certificate configuration; do not disable SSL verification.

## Next improvements
LLM Pydantic extraction, LlamaIndex RouterQueryEngine, source-line chunk citations, incremental sync/delete, contradiction and recency resolution, stronger evaluation datasets and retry-query rewriting.
