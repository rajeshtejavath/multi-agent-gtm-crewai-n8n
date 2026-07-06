import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";
import { searchWeb } from "./tools/search.js";
import { scrapeUrl } from "./tools/scrape.js";
import { saveEvidence, getEvidence } from "./tools/evidence.js";
import { exportToDocs } from "./tools/docs.js";

dotenv.config({ path: "../../.env" });

const server = new Server(
  { name: "research-mcp-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "search_web",
      description:
        "Search the web using SerpAPI and return structured results with titles, URLs, and snippets",
      inputSchema: {
        type: "object",
        properties: {
          query: { type: "string", description: "Search query" },
          num_results: {
            type: "number",
            description: "Number of results (default 10)",
          },
        },
        required: ["query"],
      },
    },
    {
      name: "scrape_url",
      description:
        "Fetch and extract main text content from a URL, returning clean text",
      inputSchema: {
        type: "object",
        properties: {
          url: { type: "string", description: "URL to scrape" },
        },
        required: ["url"],
      },
    },
    {
      name: "save_evidence",
      description:
        "Save a research finding with citation to the evidence store",
      inputSchema: {
        type: "object",
        properties: {
          topic: { type: "string", description: "Research topic/category" },
          finding: { type: "string", description: "The research finding" },
          source_url: { type: "string", description: "Source URL" },
          source_title: { type: "string", description: "Source title" },
          confidence: {
            type: "string",
            enum: ["high", "medium", "low"],
            description: "Confidence in the finding",
          },
        },
        required: ["topic", "finding", "source_url", "source_title"],
      },
    },
    {
      name: "get_evidence",
      description:
        "Retrieve all stored evidence for a topic or all topics",
      inputSchema: {
        type: "object",
        properties: {
          topic: {
            type: "string",
            description: "Topic to filter by (optional, returns all if empty)",
          },
        },
      },
    },
    {
      name: "export_to_docs",
      description:
        "Export content to Google Docs, creating a formatted document",
      inputSchema: {
        type: "object",
        properties: {
          title: { type: "string", description: "Document title" },
          content: {
            type: "string",
            description: "Markdown content to export",
          },
        },
        required: ["title", "content"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "search_web": {
        const results = await searchWeb(args.query, args.num_results || 10);
        return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
      }
      case "scrape_url": {
        const text = await scrapeUrl(args.url);
        return { content: [{ type: "text", text }] };
      }
      case "save_evidence": {
        const result = await saveEvidence(args);
        return { content: [{ type: "text", text: JSON.stringify(result) }] };
      }
      case "get_evidence": {
        const evidence = await getEvidence(args.topic);
        return { content: [{ type: "text", text: JSON.stringify(evidence, null, 2) }] };
      }
      case "export_to_docs": {
        const docUrl = await exportToDocs(args.title, args.content);
        return { content: [{ type: "text", text: docUrl }] };
      }
      default:
        return { content: [{ type: "text", text: `Unknown tool: ${name}` }], isError: true };
    }
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Research MCP Server running on stdio");
}

main().catch(console.error);
