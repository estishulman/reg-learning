import argparse
import json
import os
from pathlib import Path
from .indexing import build_index, existing_index
from .extraction import extract

def main():
    parser = argparse.ArgumentParser(description="Agentic coding knowledge RAG")
    parser.add_argument("command", choices=["index", "extract", "chat"])
    parser.add_argument("--root", default=os.getenv("PROJECT_ROOT", "sample_project"))
    args = parser.parse_args()
    if args.command == "index":
        _, files, nodes = build_index(args.root)
        print(f"Indexed {files} files, {nodes} chunks")
    elif args.command == "extract":
        data = extract(args.root)
        print({key: len(value) for key, value in data["items"].items()})
    else:
        import gradio as gr
        from llama_index.llms.cohere import Cohere
        from .config import require
        from .workflow import QueryWorkflow
        data_path = Path("output/knowledge.json")
        data = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else None
        workflow = QueryWorkflow(existing_index(), Cohere(api_key=require("COHERE_API_KEY"), model=os.getenv("COHERE_LLM_MODEL", "command-r-plus")), data)
        def respond(message, history):
            result = workflow.run(message)
            sources = "\n".join(f'- {s.get("file", "unknown")} ({s.get("tool", "")})' for s in result.sources)
            return result.answer + ("\n\nSources:\n" + sources if sources else "")
        gr.ChatInterface(fn=respond, title="Agentic Coding Knowledge RAG", description="Ask questions about Cursor, Claude Code and Kiro Markdown knowledge").launch()
if __name__ == "__main__":
    main()
