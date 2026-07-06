# Multi-Agent Market Research & GTM Planning

## Capstone Project: n8n, MCP, and CrewAI

A multi-agent workflow system that automates market research and go-to-market (GTM) planning for the **AI Coding Tools** market. Implemented in both **n8n** (visual workflow) and **CrewAI** (Python framework) for comparison.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PROJECT BRIEF INPUT                       │
│  "Research AI coding tools market, create GTM plan..."       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    HEAD PLANNER AGENT                         │
│  • Decomposes brief into research questions                  │
│  • Identifies competitors to analyze                         │
│  • Selects analytical frameworks                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   RESEARCH AGENT                              │
│  Tools: search_web, scrape_url, save_evidence                │
│  • Searches web for each research question                   │
│  • Scrapes relevant pages                                    │
│  • Saves findings with citations                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   ANALYST AGENT                               │
│  • Builds competitor comparison matrix                       │
│  • Creates pricing tables                                    │
│  • Performs SWOT analysis                                    │
│  • Estimates market sizing (TAM/SAM/SOM)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   STRATEGY AGENT                              │
│  Tools: export_to_docs                                       │
│  • Defines ICPs and personas                                 │
│  • Crafts value proposition                                  │
│  • Plans channel strategy                                    │
│  • Creates 90-day launch plan                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   GOOGLE DOCS EXPORT                          │
│  • Formatted GTM strategy document                           │
│  • PDF export option                                         │
└─────────────────────────────────────────────────────────────┘
```

### MCP Server (Shared Foundation)

The MCP (Model Context Protocol) server provides tools to both implementations:

| Tool | Purpose |
|------|---------|
| `search_web` | Searches Google via SerpAPI, returns structured results |
| `scrape_url` | Extracts text content from URLs |
| `save_evidence` | Stores findings with citations in JSON |
| `get_evidence` | Retrieves stored research evidence |
| `export_to_docs` | Creates formatted Google Docs |

---

## Setup Instructions (Ubuntu VM)

### Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install n8n
sudo npm install -g n8n

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install UV (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Install CrewAI
pip install crewai crewai-tools
```

### API Keys Setup

1. **OpenAI API Key** — https://platform.openai.com/api-keys
   - Create account → API Keys → Create new secret key
   - Needed for: GPT-4o (powers all 4 agents)

2. **SerpAPI Key** — https://serpapi.com
   - Sign up → Dashboard → API Key
   - Free tier: 100 searches/month (sufficient for testing)

3. **Google Docs API** — Google Cloud Console
   - Create project → Enable Google Docs API & Google Drive API
   - Create Service Account → Download JSON credentials
   - Share target Google Drive folder with service account email

### Environment Configuration

```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Set your keys:
# OPENAI_API_KEY=sk-...
# SERPAPI_API_KEY=...
# GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
```

---

## n8n Implementation

### Running n8n

```bash
# Start n8n
n8n start

# Open browser: http://localhost:5678
```

### Importing the Workflow

1. Open n8n UI → Workflows → Import from File
2. Select `n8n-workflow/gtm-planning-workflow.json`
3. Configure credentials:
   - OpenAI: Settings → Credentials → Add OpenAI credential
   - Google Docs: Settings → Credentials → Add Google OAuth2

### Workflow Nodes

| Node | Type | Purpose |
|------|------|---------|
| Manual Trigger | Trigger | Starts workflow execution |
| Set Project Brief | Set | Configures the research brief |
| Head Planner Agent | OpenAI | Decomposes brief into research plan |
| Research Agent | OpenAI | Collects evidence with citations |
| Analyst Agent | OpenAI | Creates frameworks and matrices |
| Strategy Agent | OpenAI | Drafts complete GTM plan |
| Create Google Doc | HTTP | Exports plan to Google Docs |
| Log Completion | Set | Records execution metrics |

### Running the Workflow

1. Click "Execute Workflow" button
2. Monitor execution in real-time
3. Check each node's output for debugging
4. Final output appears in Google Docs

---

## CrewAI Implementation

### Setup

```bash
cd crewai-gtm

# Create virtual environment with UV
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### Running the Crew

```bash
# Run with default brief (AI coding tools market)
python -m crewai_gtm.main

# Run with custom brief
python -m crewai_gtm.main "Research the CRM market and create a GTM plan for a new AI-powered CRM"
```

### Running the Chatbot

```bash
# Start Streamlit chatbot interface
streamlit run src/crewai_gtm/chatbot.py

# Open browser: http://localhost:8501
```

### Running Tests

```bash
# Run unit tests
python -m pytest tests/ -v

# Or run directly
python tests/test_tools.py
```

### Project Structure

```
crewai-gtm/
├── pyproject.toml              # Project config & dependencies
├── src/crewai_gtm/
│   ├── main.py                 # CLI entry point
│   ├── crew.py                 # Crew orchestration
│   ├── chatbot.py              # Streamlit UI
│   ├── agents/                 # Agent definitions
│   ├── tasks/                  # Task definitions
│   ├── tools/                  # Custom tools (search, scrape, evidence, docs)
│   ├── config/
│   │   ├── agents.yaml         # Agent roles & backstories
│   │   └── tasks.yaml          # Task descriptions & outputs
│   └── outputs/                # Generated files
└── tests/                      # Unit & integration tests
```

---

## MCP Server

### Starting the Server

```bash
cd mcp-server
npm install
npm start
```

### Testing Tools with curl

```bash
# Test search
echo '{"method":"tools/call","params":{"name":"search_web","arguments":{"query":"AI coding tools 2024"}}}' | node src/index.js

# Test evidence storage
echo '{"method":"tools/call","params":{"name":"save_evidence","arguments":{"topic":"pricing","finding":"Cursor Pro costs $20/month","source_url":"https://cursor.sh/pricing","source_title":"Cursor Pricing"}}}' | node src/index.js
```

---

## Testing

### Unit Tests (Mocked)

```bash
cd crewai-gtm
python tests/test_tools.py
```

Tests cover:
- ✅ SerpAPI search returns structured results
- ✅ URL scraping extracts content correctly
- ✅ Evidence save/retrieve works
- ✅ Google Docs export falls back to local file

### Scenario Test (Golden Brief)

```
Input: "Research the AI coding tools market (Cursor, GitHub Copilot, Claude Code, 
Windsurf, Amazon CodeWhisperer). Create a GTM plan for launching a new AI pair 
programming tool targeting enterprise development teams."

Expected outputs:
- 8+ research questions answered
- 5+ competitors in comparison matrix
- Complete SWOT analysis
- 3+ ICP personas defined
- 90-day launch timeline
- All claims cited with source URLs
```

### KPI Validation

| KPI | Target | How to Measure |
|-----|--------|----------------|
| Coverage | ≥90% questions answered | Count answered / total |
| Source quality | ≥80% top-tier sources | Manual review |
| Latency | <15 minutes | Time full execution |
| Strategy quality | ≥4/5 rubric | Human evaluation |
| Reproducibility | ≥80% consistent | Run 3x, compare |
| Cost | Within budget | Log token usage |

---

## Comparison: n8n vs CrewAI

| Criteria | n8n | CrewAI |
|----------|-----|--------|
| **Setup complexity** | Medium (UI-based, needs browser) | Low (Python package, CLI) |
| **Flexibility** | Limited by node types | Highly flexible (code) |
| **Debugging** | Visual node inspection | Print/logging, IDE debugger |
| **MCP Integration** | Via HTTP/custom nodes | Native Python tools |
| **Observability** | Built-in execution logs | Custom logging (see `crew_run.log`) |
| **Scalability** | Enterprise features available | Custom scaling required |
| **Learning curve** | Low (visual) | Medium (Python/YAML) |
| **Cost** | n8n cloud pricing | Only API costs |
| **Reproducibility** | High (deterministic flow) | Medium (LLM variation) |
| **Best for** | Non-technical teams, quick prototypes | Developers, complex logic |

### Detailed Comparison Results

| Metric | n8n Implementation | CrewAI Implementation |
|--------|-------------------|----------------------|
| **Execution time** | ~3-5 min (estimated) | ~8-12 min (with web research) |
| **Token usage** | ~32K tokens (4 LLM calls) | ~50K+ tokens (multi-turn agent loops) |
| **Cost per run** | ~$0.30 (GPT-4o) | ~$0.00 (Groq free tier) |
| **Evidence collected** | LLM-generated (no real search) | 16 real web sources scraped |
| **Tool integration** | HTTP nodes → MCP server | Native Python tool functions |
| **Error handling** | Built-in retry (3x per node) | `max_retry_limit=3` per agent |
| **Logging** | n8n execution history | Python logging + `crew_run.log` |
| **Agent autonomy** | Fixed prompts, no tool choice | Agents choose tools dynamically |
| **Quality** | Good (structured prompts) | Higher (real evidence + reasoning) |

### Key Findings

1. **n8n is faster to set up** — Visual drag-and-drop, no coding required
2. **CrewAI produces richer output** — Agents use real tools (web search, scraping) to gather actual evidence
3. **n8n has better observability** — Built-in execution logs and node-level debugging
4. **CrewAI is more flexible** — Custom tools, dynamic agent behavior, Python extensibility
5. **Both need API budget management** — Rate limits are the primary constraint for free-tier usage

---

## Deliverables Checklist

- [x] Exported n8n workflow JSON file (`n8n-workflow/gtm-planning-workflow.json`)
- [x] CrewAI project files in UV structure (`crewai-gtm/`)
- [x] Sample GTM plan output (`docs/GTM_Plan_AI_Coding_Tools.md`)
- [x] Research evidence with citations (`crewai-gtm/src/crewai_gtm/outputs/evidence.json`)
- [x] CrewAI chatbot screenshots (`docs/screenshots/`)
- [x] Documentation / README (this file)
- [x] Logging, retries, and cost tracking (`crew.py` + `crew_run.log`)

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `SERPAPI_API_KEY not set` | Check `.env` file exists and is loaded |
| `OpenAI rate limit` | Wait 60s, reduce `max_tokens`, or upgrade plan |
| n8n credential error | Re-add credentials in n8n Settings → Credentials |
| Google Docs permission denied | Share folder with service account email |
| CrewAI import error | Run `uv pip install -e .` in crewai-gtm directory |
| MCP server won't start | Check `npm install` completed, Node.js ≥20 |

### Error Handling

- All agents have retry logic (max 3 attempts)
- Exponential backoff on API rate limits
- Local file fallback when Google Docs unavailable
- Evidence store persists between runs

---

## Cost Estimation

| Component | Cost per Run |
|-----------|-------------|
| GPT-4o (4 agents, ~8K tokens each) | ~$0.30-0.50 |
| SerpAPI (5-10 searches) | Free tier / ~$0.01 |
| Google Docs API | Free |
| **Total per run** | **~$0.50** |

---

## License

This project is submitted as part of a certification capstone. For educational use only.
