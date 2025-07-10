import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base import BaseTool, ToolParameter, ToolResult

class WebSearchTool(BaseTool):
    """Tool for searching the web and extracting information."""
    
    name = "web_search"
    description = "Search the web for information and return relevant results"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="Search query to look up on the web"
        ),
        ToolParameter(
            name="num_results",
            type="integer",
            description="Number of search results to return",
            required=False,
            default=5
        )
    ]
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            query = kwargs.get("query")
            num_results = kwargs.get("num_results", 5)
            
            if not query:
                return ToolResult(
                    success=False,
                    error="Query parameter is required"
                )
            
            # Use DuckDuckGo for search (no API key required)
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract search results
            for i, result in enumerate(soup.find_all('div', class_='result')):
                if i >= num_results:
                    break
                    
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
            
            return ToolResult(
                success=True,
                data={
                    'query': query,
                    'results': results,
                    'total_found': len(results)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Web search failed: {str(e)}"
            )

class WebScrapeTool(BaseTool):
    """Tool for scraping content from a specific web page."""
    
    name = "web_scrape"
    description = "Extract text content from a specific web page URL"
    parameters = [
        ToolParameter(
            name="url",
            type="string",
            description="URL of the web page to scrape"
        ),
        ToolParameter(
            name="max_length",
            type="integer",
            description="Maximum length of content to return",
            required=False,
            default=5000
        )
    ]
    
    def execute(self, **kwargs) -> ToolResult:
        try:
            url = kwargs.get("url")
            max_length = kwargs.get("max_length", 5000)
            
            if not url:
                return ToolResult(
                    success=False,
                    error="URL parameter is required"
                )
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return ToolResult(
                success=True,
                data={
                    'url': url,
                    'content': text,
                    'length': len(text)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Web scraping failed: {str(e)}"
            )