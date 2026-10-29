import json
import re
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from .loader import load_markdown

CATEGORIES = {"decisions": ["decision", "decided", "הוחלט", "החלטה", "נבחר"], "rules": ["rule", "must", "always", "חובה", "כלל", "יש להשתמש"], "warnings": ["warning", "avoid", "do not", "sensitive", "רגיש", "לא לשנות", "אזהרה"]}

def extract(root, output="output/knowledge.json"):
    items = {key: [] for key in CATEGORIES}
    sources = []
    for doc in load_markdown(root):
        md = doc.metadata
        sources.append({"tool": md["tool"], "file": md["file"], "hash": "sha256:" + md["sha256"], "last_modified": md["modified_at"]})
        heading = md["heading"]
        for line_no, line in enumerate(doc.text.splitlines(), 1):
            clean = re.sub(r"^[\s#*\-]+", "", line).strip()
            if not clean or len(clean) < 12:
                continue
            for category, words in CATEGORIES.items():
                if any(word in clean.casefold() for word in words):
                    key = f'{md["file"]}:{line_no}:{category}:{clean}'
                    items[category].append({"id": sha256(key.encode()).hexdigest()[:16], "summary": clean, "title": heading, "source": {"tool": md["tool"], "file": md["file"], "line_range": [line_no, line_no]}, "observed_at": md["modified_at"]})
    data = {"schema_version": "1.0", "generated_at": datetime.now(timezone.utc).isoformat(), "sources": sources, "items": items, "extraction_method": "deterministic_keyword_baseline"}
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

def structured_search(question, data):
    q = question.casefold()
    selected = "decisions" if any(x in q for x in ["החלט", "decision"]) else "warnings" if any(x in q for x in ["רגיש", "אזהר", "warning"]) else "rules"
    rows = data["items"].get(selected, [])
    if any(x in q for x in ["אחרון", "last", "recent"]):
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        days = 7 if any(x in q for x in ["שבוע", "week"]) else 30
        rows = [r for r in rows if datetime.fromisoformat(r["observed_at"]) >= now-timedelta(days=days)]
    return rows
