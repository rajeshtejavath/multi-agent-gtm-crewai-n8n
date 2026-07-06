import { readFileSync, writeFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const EVIDENCE_FILE = join(__dirname, "../../evidence/evidence.json");

function loadEvidence() {
  if (!existsSync(EVIDENCE_FILE)) {
    return { findings: [], metadata: { created: new Date().toISOString() } };
  }
  return JSON.parse(readFileSync(EVIDENCE_FILE, "utf-8"));
}

function persistEvidence(data) {
  data.metadata.updated = new Date().toISOString();
  writeFileSync(EVIDENCE_FILE, JSON.stringify(data, null, 2));
}

export async function saveEvidence({ topic, finding, source_url, source_title, confidence = "medium" }) {
  const data = loadEvidence();

  const entry = {
    id: `ev_${Date.now()}`,
    topic,
    finding,
    source_url,
    source_title,
    confidence,
    timestamp: new Date().toISOString(),
  };

  data.findings.push(entry);
  persistEvidence(data);

  return { success: true, id: entry.id, total_findings: data.findings.length };
}

export async function getEvidence(topic) {
  const data = loadEvidence();

  if (!topic) {
    return data;
  }

  const filtered = data.findings.filter(
    (f) => f.topic.toLowerCase() === topic.toLowerCase()
  );

  return {
    topic,
    findings: filtered,
    count: filtered.length,
  };
}
