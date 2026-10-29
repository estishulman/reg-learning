from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
from llama_index.core import Document

TOOL_DIRS = {"cursor": [".cursor"], "claude_code": [".claude"], "kiro": [".kiro"]}

def load_markdown(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    docs = []
    for tool, dirs in TOOL_DIRS.items():
        for dirname in dirs:
            folder = root / dirname
            if not folder.is_dir():
                continue
            for file in sorted(folder.rglob("*.md")):
                if file.is_symlink():
                    continue
                content = file.read_text(encoding="utf-8-sig")
                if not content.strip():
                    continue
                stat = file.stat()
                docs.append(Document(text=content, metadata={
                    "tool": tool, "file": str(file.relative_to(root)),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    "sha256": sha256(content.encode()).hexdigest(),
                    "heading": next((line.lstrip("# ").strip() for line in content.splitlines() if line.startswith("#")), "")
                }))
    return docs
