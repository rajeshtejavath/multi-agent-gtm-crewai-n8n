import axios from "axios";
import * as cheerio from "cheerio";

export async function scrapeUrl(url) {
  const response = await axios.get(url, {
    timeout: 15000,
    headers: {
      "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    },
  });

  const $ = cheerio.load(response.data);

  // Remove scripts, styles, nav, footer
  $("script, style, nav, footer, header, aside, .sidebar, .menu").remove();

  // Extract main content
  const mainContent =
    $("main").text() || $("article").text() || $("body").text();

  // Clean up whitespace
  const cleanText = mainContent
    .replace(/\s+/g, " ")
    .replace(/\n\s*\n/g, "\n")
    .trim()
    .slice(0, 5000); // Limit to 5000 chars

  return JSON.stringify({
    url,
    title: $("title").text().trim(),
    content: cleanText,
    scraped_at: new Date().toISOString(),
  });
}
