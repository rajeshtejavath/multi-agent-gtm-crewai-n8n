"""Main entry point for the CrewAI GTM Planning system."""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)


DEFAULT_BRIEF = """
Research the AI coding tools market (Cursor, GitHub Copilot, Claude Code, Windsurf,
Amazon CodeWhisperer/Q Developer, Cody by Sourcegraph, Tabnine, Replit).

Create a comprehensive GTM plan for launching a new AI pair programming tool
targeting enterprise development teams with 50+ engineers. The tool differentiates
through superior codebase understanding and security-first design.

Focus areas:
- Competitor features, pricing, and market positioning
- Enterprise buyer personas and pain points
- Channel strategy for developer tools
- Pricing model recommendations
- 90-day launch timeline
"""


def run(brief: str = None):
    """Run the GTM planning crew with the given brief."""
    from .crew import GTMCrew

    project_brief = brief or DEFAULT_BRIEF

    print("=" * 60)
    print("MULTI-AGENT GTM PLANNING SYSTEM")
    print("=" * 60)
    print(f"\nProject Brief:\n{project_brief.strip()}\n")
    print("=" * 60)
    print("Starting agents...\n")

    start_time = time.time()

    crew = GTMCrew(project_brief)
    result = crew.run()

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"COMPLETED in {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print("=" * 60)

    # Save final output
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "gtm_plan_final.md"
    output_file.write_text(result)
    print(f"\nFinal GTM plan saved to: {output_file}")

    return result


if __name__ == "__main__":
    brief = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    run(brief)
