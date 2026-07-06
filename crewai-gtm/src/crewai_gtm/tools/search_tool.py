import os
import json
import requests
from crewai.tools import tool


@tool("Search Web")
def search_web(query: str) -> str:
    """Search the web using SerpAPI and return structured results with titles, URLs, and snippets."""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return json.dumps({"error": "SERPAPI_API_KEY not set"})

    response = requests.get(
        "https://serpapi.com/search",
        params={"q": query, "api_key": api_key, "engine": "google", "num": 10},
    )
    data = response.json()
    organic = data.get("organic_results", [])

    results = [
        {"title": r.get("title"), "url": r.get("link"), "snippet": r.get("snippet")}
        for r in organic[:10]
    ]
    return json.dumps({"query": query, "results": results, "count": len(results)})
