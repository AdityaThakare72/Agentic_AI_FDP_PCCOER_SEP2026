"""
Web research helpers built on Tavily.

research_web() runs one search and returns a clean list of results.
format_research() turns a list of findings into one block of text that
we can paste into a prompt.
"""

from langchain_tavily import TavilySearch


def research_web(query: str, max_results: int = 3) -> list[dict]:
    """Search the web for one query and return a list of {title, url, content}."""
    # created inside the function so the key is only needed when a search actually runs
    search = TavilySearch(max_results=max_results)
    response = search.invoke({"query": query})

    # Tavily returns a dict with a "results" list; anything else means the search failed
    if not isinstance(response, dict):
        return []

    results = []
    for item in response.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            # trim long pages so the prompt stays a reasonable size
            "content": item.get("content", "")[:1200],
        })
    return results


def format_research(findings: list[dict]) -> str:
    """Join all findings into one numbered text block for the notes prompt."""
    blocks = []
    for number, finding in enumerate(findings, start=1):
        blocks.append(
            f"[{number}] {finding['title']}\n"
            f"URL: {finding['url']}\n"
            f"Searched for: {finding['question']}\n"
            f"{finding['content']}"
        )
    return "\n\n".join(blocks)
