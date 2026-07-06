import axios from "axios";

export async function searchWeb(query, numResults = 10) {
  const apiKey = process.env.SERPAPI_API_KEY;

  if (!apiKey) {
    throw new Error("SERPAPI_API_KEY not set in environment variables");
  }

  const response = await axios.get("https://serpapi.com/search", {
    params: {
      q: query,
      api_key: apiKey,
      engine: "google",
      num: numResults,
    },
  });

  const organicResults = response.data.organic_results || [];

  return {
    query,
    timestamp: new Date().toISOString(),
    results: organicResults.map((r) => ({
      title: r.title,
      url: r.link,
      snippet: r.snippet,
      position: r.position,
    })),
    total_results: organicResults.length,
  };
}
