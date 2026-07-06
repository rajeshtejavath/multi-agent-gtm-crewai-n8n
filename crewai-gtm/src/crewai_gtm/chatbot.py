"""Streamlit chatbot interface for the CrewAI GTM Planning system."""
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

import streamlit as st


def main():
    st.set_page_config(
        page_title="AI GTM Planner",
        page_icon="🎯",
        layout="wide",
    )

    st.title("🎯 Multi-Agent GTM Planning System")
    st.markdown(
        "Enter a project brief and watch the AI agents research the market, "
        "analyze competitors, and create a go-to-market strategy."
    )

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        serpapi_key = st.text_input("SerpAPI Key", type="password", value=os.getenv("SERPAPI_API_KEY", ""))

        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if serpapi_key:
            os.environ["SERPAPI_API_KEY"] = serpapi_key

        st.divider()
        st.markdown("### Agents")
        st.markdown("1. 🧠 **Head Planner** - Orchestrates research")
        st.markdown("2. 🔍 **Research Agent** - Searches & collects evidence")
        st.markdown("3. 📊 **Analyst Agent** - Creates frameworks & tables")
        st.markdown("4. 🎯 **Strategy Agent** - Drafts GTM plan")

    # Main input
    default_brief = (
        "Research the AI coding tools market (Cursor, GitHub Copilot, Claude Code, "
        "Windsurf, CodeWhisperer). Create a GTM plan for a new AI pair programming "
        "tool targeting enterprise dev teams."
    )

    brief = st.text_area(
        "Project Brief",
        value=default_brief,
        height=150,
        help="Describe the market to research and the product to plan for.",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        run_button = st.button("🚀 Run Agents", type="primary")

    if run_button:
        if not os.getenv("OPENAI_API_KEY"):
            st.error("Please set your OpenAI API key in the sidebar.")
            return
        if not os.getenv("SERPAPI_API_KEY"):
            st.error("Please set your SerpAPI key in the sidebar.")
            return

        with st.status("Running multi-agent workflow...", expanded=True) as status:
            st.write("🧠 Head Planner: Decomposing project brief...")

            from crewai_gtm.crew import GTMCrew
            import time

            start = time.time()
            crew = GTMCrew(brief)

            try:
                result = crew.run()
                elapsed = time.time() - start

                status.update(label=f"Completed in {elapsed:.0f}s", state="complete")

                st.success(f"GTM plan generated in {elapsed/60:.1f} minutes!")

                st.markdown("## Generated GTM Plan")
                st.markdown(result)

                # Download button
                st.download_button(
                    label="📥 Download GTM Plan (Markdown)",
                    data=result,
                    file_name="gtm_plan.md",
                    mime="text/markdown",
                )

            except Exception as e:
                status.update(label="Error", state="error")
                st.error(f"Error: {str(e)}")

    # Show previous outputs if they exist
    output_file = Path(__file__).parent / "outputs" / "gtm_plan_final.md"
    if output_file.exists() and not run_button:
        with st.expander("📄 Previous GTM Plan Output"):
            st.markdown(output_file.read_text())


if __name__ == "__main__":
    main()
