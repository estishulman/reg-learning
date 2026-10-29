from dataclasses import dataclass, field
from typing import Any

@dataclass
class QueryEvent:
    question: str

@dataclass
class RetrievedEvent:
    nodes: list[Any]
    query: str

@dataclass
class AnswerEvent:
    answer: str
    sources: list[dict] = field(default_factory=list)

@dataclass
class State:
    attempts: int = 0
    route: str = "semantic"
    warnings: list[str] = field(default_factory=list)

class QueryWorkflow:
    """Explicit event-driven state machine; steps have typed event inputs/outputs."""
    def __init__(self, index, llm, structured_data=None, threshold=0.25):
        self.index = index
        self.llm = llm
        self.data = structured_data
        self.threshold = threshold
        self.state = State()

    def validate(self, event: QueryEvent):
        if not event.question.strip():
            return AnswerEvent("יש להזין שאלה.")
        return event

    def route(self, event: QueryEvent):
        q = event.question.casefold()
        structured = any(word in q for word in ("כל ההחלטות", "רשימת", "שבוע האחרון", "חודש האחרון", "all decisions", "list all"))
        self.state.route = "structured" if structured and self.data else "semantic"
        return event

    def retrieve(self, event: QueryEvent):
        retriever = self.index.as_retriever(similarity_top_k=6)
        nodes = retriever.retrieve(event.question)
        nodes = [node for node in nodes if node.score is None or node.score >= self.threshold]
        return RetrievedEvent(nodes, event.question)

    def synthesize(self, event: RetrievedEvent):
        if not event.nodes:
            return AnswerEvent("לא נמצא מידע מספיק במקורות כדי לענות בביטחון.")
        from llama_index.core.response_synthesizers import get_response_synthesizer
        synthesizer = get_response_synthesizer(llm=self.llm, response_mode="compact")
        result = synthesizer.synthesize(event.query, nodes=event.nodes)
        return AnswerEvent(str(result), [{"file": n.node.metadata.get("file"), "tool": n.node.metadata.get("tool"), "score": n.score} for n in event.nodes])

    def run(self, question):
        from .extraction import structured_search
        self.state = State()
        event = self.validate(QueryEvent(question))
        if isinstance(event, AnswerEvent):
            return event
        event = self.route(event)
        if self.state.route == "structured":
            rows = structured_search(question, self.data)
            if not rows:
                return AnswerEvent("לא נמצאו פריטים מובנים מתאימים.")
            evidence = "\n".join(f'{r["summary"]} (source: {r["source"]["file"]}, line {r["source"]["line_range"][0]})' for r in rows)
            prompt = f"Answer in the user's language using ONLY these extracted records. Mention uncertainty.\nQuestion: {question}\nRecords:\n{evidence}"
            return AnswerEvent(str(self.llm.complete(prompt)), [r["source"] for r in rows])
        event = self.retrieve(event)
        if not event.nodes:
            self.state.attempts += 1
            event = self.retrieve(QueryEvent(question + " documentation specifications decisions"))
        return self.synthesize(event)
