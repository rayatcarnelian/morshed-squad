import time
import urllib.request
import urllib.parse
import json
from pydantic import Field, BaseModel
from typing import Type
from crewai.tools import BaseTool

class WebSearchSchema(BaseModel):
    """Input for WebSearchTool."""
    search_query: str = Field(..., description="The query to search the web for.")

class MorshedWebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = "A tool that can search the internet for live information. Useful for finding current trends, news, or specific product data."
    args_schema: Type[BaseModel] = WebSearchSchema

    def _run(self, search_query: str) -> str:
        """Search the web using Wikipedia's public Open API."""
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_query)}&utf8=&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read())
            
            results = []
            for r in data.get('query', {}).get('search', [])[:5]:
                # Wikipedia snippets contain HTML span tags, remove them for cleaner console output
                clean_snippet = r['snippet'].replace('<span class="searchmatch">', '').replace('</span>', '')
                results.append(f"Title: {r['title']}\nURL: https://en.wikipedia.org/wiki/{urllib.parse.quote(r['title'])}\nSnippet: {clean_snippet}...\n---")
            
            if not results:
                return f"No useful results found for '{search_query}'. Try a broader search term."
                
            return "\n".join(results)
        except Exception as e:
            return f"Error occurred during web search: {str(e)}"
