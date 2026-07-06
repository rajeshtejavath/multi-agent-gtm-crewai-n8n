import yaml
import logging
import time
import litellm
from pathlib import Path
from crewai import Agent, Crew, Task, Process, LLM

litellm.drop_params = True

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / "outputs" / "crew_run.log"),
    ],
)
logger = logging.getLogger("GTMCrew")

# --- Cost & Latency Tracking ---
_call_metrics = {"calls": 0, "total_tokens": 0, "start_time": None}

_original_completion = litellm.completion


def _patched_completion(*args, **kwargs):
    """Strip unsupported Anthropic cache fields and track metrics."""
    if "messages" in kwargs:
        for msg in kwargs["messages"]:
            msg.pop("cache_breakpoint", None)
            msg.pop("cache_control", None)

    _call_metrics["calls"] += 1
    start = time.time()

    response = _original_completion(*args, **kwargs)

    elapsed = time.time() - start
    tokens = getattr(response, "usage", None)
    if tokens:
        _call_metrics["total_tokens"] += tokens.total_tokens
        logger.info(
            f"LLM call #{_call_metrics['calls']}: "
            f"{tokens.total_tokens} tokens, {elapsed:.1f}s"
        )
    return response


litellm.completion = _patched_completion

from .tools.search_tool import search_web
from .tools.scrape_tool import scrape_url
from .tools.evidence_tool import save_evidence, get_evidence
from .tools.docs_tool import export_to_docs

CONFIG_DIR = Path(__file__).parent / "config"

gemini_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.7,
    drop_params=True,
)


def load_config(filename: str) -> dict:
    with open(CONFIG_DIR / filename) as f:
        return yaml.safe_load(f)


class GTMCrew:
    def __init__(self, project_brief: str):
        self.project_brief = project_brief
        self.agents_config = load_config("agents.yaml")
        self.tasks_config = load_config("tasks.yaml")
        logger.info("GTMCrew initialized with brief: %s...", project_brief[:80])

    def _create_agents(self) -> dict:
        cfg = self.agents_config

        head_planner = Agent(
            role=cfg["head_planner"]["role"],
            goal=cfg["head_planner"]["goal"],
            backstory=cfg["head_planner"]["backstory"],
            llm=gemini_llm,
            verbose=True,
            allow_delegation=False,
            max_retry_limit=3,
        )

        research_agent = Agent(
            role=cfg["research_agent"]["role"],
            goal=cfg["research_agent"]["goal"],
            backstory=cfg["research_agent"]["backstory"],
            llm=gemini_llm,
            tools=[search_web, scrape_url, save_evidence],
            verbose=True,
            max_retry_limit=3,
        )

        analyst_agent = Agent(
            role=cfg["analyst_agent"]["role"],
            goal=cfg["analyst_agent"]["goal"],
            backstory=cfg["analyst_agent"]["backstory"],
            llm=gemini_llm,
            tools=[get_evidence],
            verbose=True,
            max_retry_limit=3,
        )

        strategy_agent = Agent(
            role=cfg["strategy_agent"]["role"],
            goal=cfg["strategy_agent"]["goal"],
            backstory=cfg["strategy_agent"]["backstory"],
            llm=gemini_llm,
            tools=[export_to_docs],
            verbose=True,
            max_retry_limit=3,
        )

        logger.info("Created 4 agents: Head Planner, Research, Analyst, Strategy")
        return {
            "head_planner": head_planner,
            "research": research_agent,
            "analyst": analyst_agent,
            "strategy": strategy_agent,
        }

    def _create_tasks(self, agents: dict) -> list:
        cfg = self.tasks_config

        planning = Task(
            description=cfg["planning_task"]["description"].format(
                project_brief=self.project_brief
            ),
            expected_output=cfg["planning_task"]["expected_output"],
            agent=agents["head_planner"],
        )

        research = Task(
            description=cfg["research_task"]["description"].format(
                research_plan="{planning_output}"
            ),
            expected_output=cfg["research_task"]["expected_output"],
            agent=agents["research"],
            context=[planning],
        )

        analysis = Task(
            description=cfg["analysis_task"]["description"].format(
                research_evidence="{research_output}",
                competitors="{competitors}",
            ),
            expected_output=cfg["analysis_task"]["expected_output"],
            agent=agents["analyst"],
            context=[research],
        )

        strategy = Task(
            description=cfg["strategy_task"]["description"].format(
                market_analysis="{analysis_output}"
            ),
            expected_output=cfg["strategy_task"]["expected_output"],
            agent=agents["strategy"],
            context=[analysis],
        )

        logger.info("Created 4 tasks: Planning → Research → Analysis → Strategy")
        return [planning, research, analysis, strategy]

    def create_crew(self) -> Crew:
        agents = self._create_agents()
        tasks = self._create_tasks(agents)

        return Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

    def run(self) -> str:
        _call_metrics["start_time"] = time.time()
        logger.info("Starting crew execution...")

        crew = self.create_crew()
        result = crew.kickoff()

        elapsed = time.time() - _call_metrics["start_time"]
        logger.info(
            "Crew completed: %.1f seconds, %d LLM calls, %d total tokens",
            elapsed,
            _call_metrics["calls"],
            _call_metrics["total_tokens"],
        )
        return str(result)
