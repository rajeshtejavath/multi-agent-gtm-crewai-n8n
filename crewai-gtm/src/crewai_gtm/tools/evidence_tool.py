import os
import json
from pathlib import Path
from crewai.tools import tool

EVIDENCE_DIR = Path(__file__).parent.parent / "outputs"


def _load_evidence() -> dict:
    filepath = EVIDENCE_DIR / "evidence.json"
    if filepath.exists():
        return json.loads(filepath.read_text())
    return {"findings": [], "metadata": {"created": ""}}


def _save_evidence(data: dict):
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    filepath = EVIDENCE_DIR / "evidence.json"
    filepath.write_text(json.dumps(data, indent=2))


@tool("Save Evidence")
def save_evidence(topic: str, finding: str, source_url: str, source_title: str, confidence: str = "medium") -> str:
    """Save a research finding with citation to the evidence store. Confidence: high, medium, low."""
    data = _load_evidence()
    entry = {
        "id": f"ev_{len(data['findings']) + 1:04d}",
        "topic": topic,
        "finding": finding,
        "source_url": source_url,
        "source_title": source_title,
        "confidence": confidence,
    }
    data["findings"].append(entry)
    _save_evidence(data)
    return json.dumps({"saved": True, "id": entry["id"], "total": len(data["findings"])})


@tool("Get Evidence")
def get_evidence(topic: str = "") -> str:
    """Retrieve stored evidence, optionally filtered by topic."""
    data = _load_evidence()
    if topic:
        filtered = [f for f in data["findings"] if f["topic"].lower() == topic.lower()]
        return json.dumps({"topic": topic, "findings": filtered, "count": len(filtered)})
    return json.dumps(data)
