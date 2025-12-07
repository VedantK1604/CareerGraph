"""Web search utility using Serper API for real-time resource discovery."""
import os
from typing import List, Dict, Optional
import httpx
import validators
import requests


class SerperSearchTool:
    """Tool for searching the web using Serper/SerpAPI."""
    
    def __init__(self):
        """Initialize search tool with API key."""
        self.api_key = os.getenv("SERPER_API_KEY")
        self.search_enabled = os.getenv("SEARCH_ENABLED", "true").lower() == "true"
        
        if not self.api_key and self.search_enabled:
            print("Warning: SERPER_API_KEY not set. Web search will be disabled.")
            self.search_enabled = False
    
    async def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible and valid."""
        if not validators.url(url):
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.head(url, follow_redirects=True)
                return response.status_code < 400
        except Exception:
            return False
    
    def search_youtube(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for YouTube videos."""
        if not self.search_enabled:
            return []
        
        try:
            search_query = f"{query} tutorial 2025 site:youtube.com"
            
            # Use Serper JSON API
            import requests
            url = "https://google.serper.dev/search"
            payload = {
                "q": search_query,
                "num": max_results
            }
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"Serper API error: {response.status_code} - {response.text}")
                return []
            
            results = response.json()
            
            videos = []
            for result in results.get("organic", [])[:max_results]:
                if "youtube.com" in result.get("link", ""):
                    videos.append({
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "description": result.get("snippet", ""),
                        "type": "video",
                        "source": "YouTube"
                    })
            
            return videos
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []
    
    def search_courses(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for online courses on Coursera, Udemy, edX."""
        if not self.search_enabled:
            return []
        
        try:
            platforms = ["coursera.org", "udemy.com", "edx.org"]
            courses = []
            
            url = "https://google.serper.dev/search"
            
            for platform in platforms:
                search_query = f"{query} course site:{platform}"
                payload = {"q": search_query, "num": 2}
                headers = {
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    results = response.json()
                    for result in results.get("organic", [])[:2]:
                        courses.append({
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "description": result.get("snippet", ""),
                            "type": "course",
                            "source": platform.split('.')[0].title()
                        })
                
                if len(courses) >= max_results:
                    break
            
            return courses[:max_results]
        except Exception as e:
            print(f"Course search error: {e}")
            return []
    
    def search_documentation(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search for official documentation and guides."""
        if not self.search_enabled:
            return []
        
        try:
            search_query = f"{query} official documentation"
            
            url = "https://google.serper.dev/search"
            payload = {"q": search_query, "num": max_results}
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                return []
            
            results = response.json()
            
            docs = []
            for result in results.get("organic", [])[:max_results]:
                link = result.get("link", "")
                # Prioritize official docs domains
                if any(term in link for term in ["docs.", "documentation", "guide", "readthedocs", "github.io"]):
                    docs.append({
                        "title": result.get("title", ""),
                        "url": link,
                        "description": result.get("snippet", ""),
                        "type": "documentation",
                        "source": "Official Docs"
                    })
            
            return docs
        except Exception as e:
            print(f"Documentation search error: {e}")
            return []
    
    def search_books(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search for recommended technical books."""
        if not self.search_enabled:
            return []
        
        try:
            # Search for highly-rated technical books
            search_query = f"{query} book programming technical best recommended"
            
            url = "https://google.serper.dev/search"
            payload = {"q": search_query, "num": max_results + 2}
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"Book search error: {response.status_code}")
                return []
            
            results = response.json()
            
            books = []
            for result in results.get("organic", []):
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Filter for book-related results
                if any(term in title.lower() or term in snippet.lower() 
                      for term in ["book", "edition", "author", "published", "isbn"]):
                    books.append({
                        "title": title,
                        "url": link,
                        "description": snippet,
                        "type": "book",
                        "source": "Book"
                    })
                
                if len(books) >= max_results:
                    break
            
            return books[:max_results]
        except Exception as e:
            print(f"Book search error: {e}")
            return []
    
    def search_general(self, query: str, max_results: int = 5) -> List[Dict]:
        """General web search for resources."""
        if not self.search_enabled:
            return []
        
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": max_results,
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            resources = []
            for result in results.get("organic_results", [])[:max_results]:
                resources.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "description": result.get("snippet", ""),
                    "type": "article",
                    "source": "Web"
                })
            
            return resources
        except Exception as e:
            print(f"General search error: {e}")
            return []
    
    def search_trending(self, domain: str) -> List[str]:
        """Search for trending topics in a domain."""
        if not self.search_enabled:
            return []
        
        try:
            search_query = f"latest trends in {domain} 2025"
            params = {
                "q": search_query,
                "api_key": self.api_key,
                "num": 5,
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract trending topics from titles and snippets
            trends = []
            for result in results.get("organic_results", [])[:5]:
                snippet = result.get("snippet", "")
                # Simple extraction - in production, use NLP
                if snippet:
                    trends.append(snippet)
            
            return trends
        except Exception as e:
            print(f"Trending search error: {e}")
            return []
    
    async def search_all_types(self, topic: str) -> Dict[str, List[Dict]]:
        """Search for all resource types for a given topic."""
        if not self.search_enabled:
            return {
                "videos": [],
                "courses": [],
                "documentation": [],
                "general": []
            }
        
        return {
            "videos": self.search_youtube(topic, max_results=3),
            "courses": self.search_courses(topic, max_results=2),
            "documentation": self.search_documentation(topic, max_results=2),
        }
