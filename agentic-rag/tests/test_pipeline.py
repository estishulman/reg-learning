from pathlib import Path
from agentic_rag.loader import load_markdown
from agentic_rag.extraction import extract, structured_search
from agentic_rag.workflow import QueryWorkflow

ROOT = Path(__file__).resolve().parents[1] / "sample_project"

def test_two_tools():
    docs = load_markdown(ROOT)
    assert {d.metadata["tool"] for d in docs} == {"cursor", "claude_code"}

def test_extract(tmp_path):
    data = extract(ROOT, tmp_path / "knowledge.json")
    assert data["items"]["decisions"]
    assert data["items"]["rules"]
    assert data["items"]["warnings"]
    assert structured_search("כל ההחלטות", data)

def test_empty_question():
    result = QueryWorkflow(None, None).run("  ")
    assert "שאלה" in result.answer
