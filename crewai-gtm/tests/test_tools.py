"""Unit tests for CrewAI GTM tools."""
import json
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_search_web_returns_results():
    """Test that search_web returns structured results."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "organic_results": [
            {"title": "Cursor AI", "link": "https://cursor.sh", "snippet": "AI code editor"},
            {"title": "GitHub Copilot", "link": "https://copilot.github.com", "snippet": "AI pair programmer"},
        ]
    }

    with patch("requests.get", return_value=mock_response):
        from crewai_gtm.tools.search_tool import search_web
        result = search_web.run(query="AI coding tools")
        data = json.loads(result)

        assert data["count"] == 2
        assert data["results"][0]["title"] == "Cursor AI"
        assert "url" in data["results"][0]


def test_scrape_url_extracts_content():
    """Test that scrape_url extracts text from HTML."""
    mock_response = MagicMock()
    mock_response.text = """
    <html><head><title>Test Page</title></head>
    <body><main><p>Important content here.</p></main></body></html>
    """

    with patch("requests.get", return_value=mock_response):
        from crewai_gtm.tools.scrape_tool import scrape_url
        result = scrape_url.run(url="https://example.com")
        data = json.loads(result)

        assert "Important content" in data["content"]
        assert data["title"] == "Test Page"


def test_save_and_get_evidence(tmp_path):
    """Test evidence save and retrieval."""
    import crewai_gtm.tools.evidence_tool as ev_module

    # Override evidence directory
    ev_module.EVIDENCE_DIR = tmp_path

    from crewai_gtm.tools.evidence_tool import save_evidence, get_evidence

    result = save_evidence.run(
        topic="pricing",
        finding="Cursor costs $20/month",
        source_url="https://cursor.sh/pricing",
        source_title="Cursor Pricing",
        confidence="high",
    )
    data = json.loads(result)
    assert data["saved"] is True

    result = get_evidence.run(topic="pricing")
    data = json.loads(result)
    assert data["count"] == 1
    assert "Cursor costs $20" in data["findings"][0]["finding"]


def test_export_to_docs_local_fallback(tmp_path):
    """Test that export falls back to local file without Google credentials."""
    import crewai_gtm.tools.docs_tool as docs_module

    docs_module.OUTPUT_DIR = tmp_path
    # Ensure no Google credentials
    import os
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    from crewai_gtm.tools.docs_tool import export_to_docs

    result = export_to_docs.run(title="Test GTM Plan", content="## Strategy\nContent here.")
    data = json.loads(result)

    assert data["success"] is True
    assert data["mode"] == "local_file"
    assert Path(data["path"]).exists()


if __name__ == "__main__":
    import tempfile

    test_search_web_returns_results()
    print("✓ test_search_web_returns_results")

    test_scrape_url_extracts_content()
    print("✓ test_scrape_url_extracts_content")

    with tempfile.TemporaryDirectory() as td:
        test_save_and_get_evidence(Path(td))
        print("✓ test_save_and_get_evidence")

    with tempfile.TemporaryDirectory() as td:
        test_export_to_docs_local_fallback(Path(td))
        print("✓ test_export_to_docs_local_fallback")

    print("\nAll tests passed!")
