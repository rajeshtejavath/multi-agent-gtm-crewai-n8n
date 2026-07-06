import { google } from "googleapis";
import { readFileSync } from "fs";

export async function exportToDocs(title, content) {
  const credPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;

  if (!credPath) {
    // Fallback: save locally as markdown if no Google credentials
    const { writeFileSync } = await import("fs");
    const { join, dirname } = await import("path");
    const { fileURLToPath } = await import("url");
    const __dirname = dirname(fileURLToPath(import.meta.url));
    const outputPath = join(__dirname, "../../evidence", `${title.replace(/\s+/g, "_")}.md`);
    writeFileSync(outputPath, `# ${title}\n\n${content}`);
    return JSON.stringify({
      success: true,
      mode: "local_file",
      path: outputPath,
      message: "Google credentials not configured. Saved as local markdown file.",
    });
  }

  const auth = new google.auth.GoogleAuth({
    keyFile: credPath,
    scopes: ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"],
  });

  const docs = google.docs({ version: "v1", auth });
  const drive = google.drive({ version: "v3", auth });

  // Create document
  const doc = await docs.documents.create({
    requestBody: { title },
  });

  const documentId = doc.data.documentId;

  // Convert markdown to Google Docs requests
  const requests = markdownToDocsRequests(content);

  if (requests.length > 0) {
    await docs.documents.batchUpdate({
      documentId,
      requestBody: { requests },
    });
  }

  // Make document accessible
  await drive.permissions.create({
    fileId: documentId,
    requestBody: { role: "reader", type: "anyone" },
  });

  const docUrl = `https://docs.google.com/document/d/${documentId}/edit`;

  return JSON.stringify({
    success: true,
    mode: "google_docs",
    document_id: documentId,
    url: docUrl,
  });
}

function markdownToDocsRequests(markdown) {
  const requests = [];
  let index = 1;

  const lines = markdown.split("\n");

  for (const line of lines) {
    let text = line;
    let style = null;

    if (line.startsWith("### ")) {
      text = line.slice(4);
      style = "HEADING_3";
    } else if (line.startsWith("## ")) {
      text = line.slice(3);
      style = "HEADING_2";
    } else if (line.startsWith("# ")) {
      text = line.slice(2);
      style = "HEADING_1";
    }

    const insertText = text + "\n";

    requests.push({
      insertText: { location: { index }, text: insertText },
    });

    if (style) {
      requests.push({
        updateParagraphStyle: {
          range: { startIndex: index, endIndex: index + insertText.length },
          paragraphStyle: { namedStyleType: style },
          fields: "namedStyleType",
        },
      });
    }

    index += insertText.length;
  }

  return requests;
}
