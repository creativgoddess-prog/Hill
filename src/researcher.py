"""
Web research engine — searches the internet for AI income methods and
scrapes key data from pages so the advisor can analyze it.
"""
import time
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from rich.console import Console

console = Console()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

RESEARCH_QUERIES = [
    "top ways to make money with AI online 2026 most successful",
    "best AI tools for making money online 2026 ChatGPT Claude comparison income",
    "AI freelancing services most in demand highest paying 2026",
    "AI content creation business $5000 per month how to start",
    "AI side hustle beginner under $300 startup cost real results 2026",
    "make money selling AI services clients 2026 step by step",
    "AI automation agency income 2026 how to start",
    "AI prompt engineering freelance income 2026",
]


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Return a list of {title, url, snippet} dicts from DuckDuckGo."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
    except Exception as e:
        console.print(f"[yellow]Search warning: {e}[/yellow]")
    return results


def scrape_page(url: str, max_chars: int = 3000) -> str:
    """Fetch a page and return its cleaned text (up to max_chars)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        # Collapse whitespace
        text = " ".join(text.split())
        return text[:max_chars]
    except Exception:
        return ""


def run_deep_research(progress_callback=None) -> dict:
    """
    Execute all research queries, scrape top results, and return a
    structured dict with raw findings the advisor can analyze.
    """
    all_findings = []
    total = len(RESEARCH_QUERIES)

    for i, query in enumerate(RESEARCH_QUERIES, 1):
        if progress_callback:
            progress_callback(i, total, query)

        results = search_web(query, max_results=4)

        for r in results[:2]:  # Scrape top 2 pages per query
            page_text = scrape_page(r["url"])
            r["page_content"] = page_text
            time.sleep(0.4)  # Polite crawl delay

        all_findings.append({
            "query": query,
            "results": results,
        })
        time.sleep(0.5)

    return {"findings": all_findings}


def format_research_for_ai(research_data: dict) -> str:
    """Flatten research data into a text block the AI can analyze."""
    lines = []
    for item in research_data["findings"]:
        lines.append(f"\n### QUERY: {item['query']}")
        for r in item["results"]:
            lines.append(f"SOURCE: {r['title']} ({r['url']})")
            lines.append(f"SNIPPET: {r['snippet']}")
            if r.get("page_content"):
                lines.append(f"PAGE CONTENT: {r['page_content'][:800]}")
            lines.append("")
    return "\n".join(lines)
