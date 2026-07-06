import os
import json
from pathlib import Path
from crewai.tools import tool

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"


@tool("Export to Google Docs")
def export_to_docs(title: str, content: str) -> str:
    """Export markdown content to Google Docs. Falls back to local file if credentials unavailable."""
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not cred_path or not Path(cred_path).exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        filename = title.replace(" ", "_") + ".md"
        filepath = OUTPUT_DIR / filename
        filepath.write_text(f"# {title}\n\n{content}")
        return json.dumps({
            "success": True,
            "mode": "local_file",
            "path": str(filepath),
            "message": "Saved locally (Google credentials not configured)",
        })

    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    credentials = service_account.Credentials.from_service_account_file(
        cred_path,
        scopes=[
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    requests_list = _markdown_to_requests(content)
    if requests_list:
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests_list}
        ).execute()

    drive_service.permissions().create(
        fileId=doc_id, body={"role": "reader", "type": "anyone"}
    ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return json.dumps({"success": True, "mode": "google_docs", "url": url, "document_id": doc_id})


def _markdown_to_requests(markdown: str) -> list:
    requests_list = []
    index = 1

    for line in markdown.split("\n"):
        text = line
        style = None

        if line.startswith("### "):
            text, style = line[4:], "HEADING_3"
        elif line.startswith("## "):
            text, style = line[3:], "HEADING_2"
        elif line.startswith("# "):
            text, style = line[2:], "HEADING_1"

        insert_text = text + "\n"
        requests_list.append({"insertText": {"location": {"index": index}, "text": insert_text}})

        if style:
            requests_list.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": index + len(insert_text)},
                    "paragraphStyle": {"namedStyleType": style},
                    "fields": "namedStyleType",
                }
            })

        index += len(insert_text)

    return requests_list
