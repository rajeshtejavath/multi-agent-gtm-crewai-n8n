import json
import requests
from bs4 import BeautifulSoup
from crewai.tools import tool


@tool("Scrape URL")
def scrape_url(url: str) -> str:
    """Fetch and extract main text content from a URL, returning clean text for analysis."""
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
        )
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        main = soup.find("main") or soup.find("article") or soup.find("body")
        text = main.get_text(separator="\n", strip=True) if main else ""
        text = text[:5000]

        return json.dumps({
            "url": url,
            "title": soup.title.string if soup.title else "",
            "content": text,
        })
    except Exception as e:
        return json.dumps({"url": url, "error": str(e)})
