"""
Open-source information retrieval system for Umbuzo.
Retrieves current and relevant information from various open sources.
"""

import logging
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
import time

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    logging.warning("BeautifulSoup not available. Install with: pip install beautifulsoup4")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OpenSourceRetriever:
    """Retrieve information from open sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.rate_limit_delay = 1.0  # Delay between requests
    
    def search_wikipedia(self, query: str, lang: str = "en") -> Optional[Dict]:
        """Search Wikipedia for information."""
        try:
            url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "wikipedia",
                    "title": data.get("title", ""),
                    "extract": data.get("extract", ""),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            logging.warning(f"Wikipedia search failed: {e}")
        
        return None
    
    def search_wikidata(self, query: str) -> Optional[Dict]:
        """Search Wikidata for structured information."""
        try:
            url = "https://www.wikidata.org/w/api.php"
            params = {
                "action": "wbsearchentities",
                "search": query,
                "language": "en",
                "format": "json",
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                entities = data.get("search", [])
                if entities:
                    entity = entities[0]
                    return {
                        "source": "wikidata",
                        "id": entity.get("id", ""),
                        "label": entity.get("label", ""),
                        "description": entity.get("description", ""),
                        "timestamp": datetime.now().isoformat(),
                    }
        except Exception as e:
            logging.warning(f"Wikidata search failed: {e}")
        
        return None
    
    def search_commoncrawl(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Common Crawl index (simplified - would need CDX API for full implementation)."""
        # Note: Full Common Crawl search requires CDX API access
        # This is a placeholder for the concept
        logging.info(f"Common Crawl search for '{query}' (placeholder)")
        return []
    
    def search_african_sources(self, query: str, country: Optional[str] = None) -> List[Dict]:
        """Search African-specific information sources."""
        results = []
        
        # Add country-specific Wikipedia searches
        if country:
            country_query = f"{country} {query}"
            wiki_result = self.search_wikipedia(country_query)
            if wiki_result:
                results.append(wiki_result)
        
        # Search general Wikipedia
        wiki_result = self.search_wikipedia(query)
        if wiki_result:
            results.append(wiki_result)
        
        # Search Wikidata
        wikidata_result = self.search_wikidata(query)
        if wikidata_result:
            results.append(wikidata_result)
        
        time.sleep(self.rate_limit_delay)  # Rate limiting
        
        return results
    
    def retrieve_current_info(self, topic: str, country: Optional[str] = None) -> Dict:
        """Retrieve current information about a topic."""
        results = {
            "topic": topic,
            "country": country,
            "sources": [],
            "timestamp": datetime.now().isoformat(),
        }
        
        # Search multiple sources
        search_query = f"{country} {topic}" if country else topic
        
        # Wikipedia
        wiki_results = self.search_african_sources(search_query, country)
        results["sources"].extend(wiki_results)
        
        return results
    
    def format_retrieved_info(self, retrieval_result: Dict) -> str:
        """Format retrieved information for model input."""
        formatted_parts = []
        
        formatted_parts.append(f"Topic: {retrieval_result['topic']}")
        if retrieval_result.get('country'):
            formatted_parts.append(f"Country: {retrieval_result['country']}")
        
        formatted_parts.append("\nRetrieved Information:")
        
        for source in retrieval_result.get("sources", []):
            source_name = source.get("source", "unknown")
            title = source.get("title") or source.get("label", "")
            content = source.get("extract") or source.get("description", "")
            
            formatted_parts.append(f"\n[{source_name}] {title}")
            formatted_parts.append(content[:500])  # Limit content length
        
        return "\n".join(formatted_parts)

class KnowledgeBase:
    """Local knowledge base with caching."""
    
    def __init__(self, cache_file: Optional[str] = None):
        self.cache_file = cache_file or r"B:\Final\knowledge_cache.json"
        self.cache = self._load_cache()
        self.retriever = OpenSourceRetriever()
    
    def _load_cache(self) -> Dict:
        """Load cached knowledge."""
        try:
            import os
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load cache: {e}")
        
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            import os
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.warning(f"Failed to save cache: {e}")
    
    def get_info(self, topic: str, country: Optional[str] = None, use_cache: bool = True) -> Dict:
        """Get information about a topic, using cache if available."""
        cache_key = f"{country}:{topic}" if country else topic
        
        # Check cache
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key]
            # Check if cache is recent (within 7 days)
            cache_time = datetime.fromisoformat(cached.get("timestamp", ""))
            age_days = (datetime.now() - cache_time).days
            if age_days < 7:
                logging.info(f"Using cached information for {cache_key}")
                return cached
        
        # Retrieve fresh information
        logging.info(f"Retrieving fresh information for {cache_key}")
        result = self.retriever.retrieve_current_info(topic, country)
        
        # Cache result
        self.cache[cache_key] = result
        self._save_cache()
        
        return result

def main():
    """Test the retrieval system."""
    kb = KnowledgeBase()
    
    test_queries = [
        ("economy", "nigeria"),
        ("history", "south africa"),
        ("population", "kenya"),
    ]
    
    print("\n=== Open Source Retrieval Test ===\n")
    for topic, country in test_queries:
        print(f"Query: {topic} in {country}")
        result = kb.get_info(topic, country)
        formatted = kb.retriever.format_retrieved_info(result)
        print(formatted)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
