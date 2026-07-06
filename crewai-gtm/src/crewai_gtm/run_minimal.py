"""Minimal pipeline run that stays under Groq's 6K token limit."""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent.parent))

import litellm
from crewai import Agent, Crew, Task, Process, LLM

litellm.drop_params = True

_original_completion = litellm.completion


def _patched_completion(*args, **kwargs):
    if "messages" in kwargs:
        for msg in kwargs["messages"]:
            msg.pop("cache_breakpoint", None)
            msg.pop("cache_control", None)
    return _original_completion(*args, **kwargs)


litellm.completion = _patched_completion

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=1000,
    drop_params=True,
)

BRIEF = "Create a short GTM plan for an AI coding tool targeting enterprise teams. Include: 3 competitors, pricing, and a 30-day launch timeline."

head_planner = Agent(
    role="Head Planner",
    goal="Create a brief research plan",
    backstory="Senior strategy consultant.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

analyst = Agent(
    role="Market Analyst",
    goal="Analyze competitors briefly",
    backstory="Former McKinsey analyst.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

strategist = Agent(
    role="GTM Strategist",
    goal="Draft a concise GTM plan",
    backstory="VP of Marketing with 10+ launches.",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

planning_task = Task(
    description=f"Analyze this brief and list 3 research questions and 3 competitors to study: {BRIEF}",
    expected_output="A short list of research questions and competitors in bullet points.",
    agent=head_planner,
)

analysis_task = Task(
    description="Create a brief competitor comparison table (3 competitors: GitHub Copilot, Cursor, Tabnine) with pricing and key features. Keep it under 200 words.",
    expected_output="A markdown table comparing 3 competitors.",
    agent=analyst,
    context=[planning_task],
)

strategy_task = Task(
    description="Write a concise 30-day GTM launch plan with pricing tiers and 3 key milestones. Keep it under 300 words.",
    expected_output="A short GTM plan with pricing and timeline.",
    agent=strategist,
    context=[analysis_task],
)

if __name__ == "__main__":
    print("=" * 50)
    print("MINIMAL GTM PIPELINE (Groq 6K token limit)")
    print("=" * 50)

    start = time.time()

    crew = Crew(
        agents=[head_planner, analyst, strategist],
        tasks=[planning_task, analysis_task, strategy_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    elapsed = time.time() - start

    print("\n" + "=" * 50)
    print(f"COMPLETED in {elapsed:.1f}s")
    print("=" * 50)
    print(str(result))

    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "minimal_run_output.md").write_text(str(result))
    print(f"\nSaved to: {output_dir / 'minimal_run_output.md'}")
