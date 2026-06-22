"""
Country Vectorizer for Umbuzo
Provides country-specific embeddings and vectorization for African context
"""

import json
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CountryVectorizer:
    """Vectorizer for country-specific data and embeddings"""

    def __init__(self, countries_file: str = "african_countries.json"):
        self.countries_file = countries_file
        self.country_data = self._load_country_data()
        self.country_embeddings = {}

    def _load_country_data(self) -> Dict:
        """Load African country data"""
        try:
            # Default African countries data
            default_countries = {
                "nigeria": {
                    "name": "Nigeria",
                    "region": "West Africa",
                    "population": 218500000,
                    "gdp_per_capita": 2300,
                    "main_languages": ["English", "Hausa", "Yoruba", "Igbo"],
                    "key_sectors": ["Oil", "Agriculture", "Technology"],
                    "political_system": "Federal Republic",
                    "independence_year": 1960
                },
                "south_africa": {
                    "name": "South Africa",
                    "region": "Southern Africa",
                    "population": 59310000,
                    "gdp_per_capita": 6000,
                    "main_languages": ["English", "Afrikaans", "Zulu", "Xhosa"],
                    "key_sectors": ["Mining", "Finance", "Tourism"],
                    "political_system": "Parliamentary Republic",
                    "independence_year": 1910
                },
                "kenya": {
                    "name": "Kenya",
                    "region": "East Africa",
                    "population": 54000000,
                    "gdp_per_capita": 1800,
                    "main_languages": ["English", "Swahili"],
                    "key_sectors": ["Agriculture", "Tourism", "Technology"],
                    "political_system": "Republic",
                    "independence_year": 1963
                },
                "ghana": {
                    "name": "Ghana",
                    "region": "West Africa",
                    "population": 31070000,
                    "gdp_per_capita": 2200,
                    "main_languages": ["English", "Twi", "Fante"],
                    "key_sectors": ["Gold Mining", "Cocoa", "Oil"],
                    "political_system": "Republic",
                    "independence_year": 1957
                },
                "egypt": {
                    "name": "Egypt",
                    "region": "North Africa",
                    "population": 104300000,
                    "gdp_per_capita": 3000,
                    "main_languages": ["Arabic", "English"],
                    "key_sectors": ["Tourism", "Agriculture", "Manufacturing"],
                    "political_system": "Republic",
                    "independence_year": 1922
                },
                "morocco": {
                    "name": "Morocco",
                    "region": "North Africa",
                    "population": 37300000,
                    "gdp_per_capita": 3200,
                    "main_languages": ["Arabic", "Berber", "French"],
                    "key_sectors": ["Tourism", "Agriculture", "Manufacturing"],
                    "political_system": "Constitutional Monarchy",
                    "independence_year": 1956
                },
                "ethiopia": {
                    "name": "Ethiopia",
                    "region": "East Africa",
                    "population": 117900000,
                    "gdp_per_capita": 900,
                    "main_languages": ["Amharic", "Oromo", "Tigrinya"],
                    "key_sectors": ["Agriculture", "Coffee", "Manufacturing"],
                    "political_system": "Federal Republic",
                    "independence_year": 1941
                },
                "tanzania": {
                    "name": "Tanzania",
                    "region": "East Africa",
                    "population": 61500000,
                    "gdp_per_capita": 1100,
                    "main_languages": ["Swahili", "English"],
                    "key_sectors": ["Agriculture", "Mining", "Tourism"],
                    "political_system": "Republic",
                    "independence_year": 1961
                },
                "uganda": {
                    "name": "Uganda",
                    "region": "East Africa",
                    "population": 47200000,
                    "gdp_per_capita": 800,
                    "main_languages": ["English", "Swahili", "Luganda"],
                    "key_sectors": ["Agriculture", "Coffee", "Oil"],
                    "political_system": "Republic",
                    "independence_year": 1962
                },
                "algeria": {
                    "name": "Algeria",
                    "region": "North Africa",
                    "population": 43850000,
                    "gdp_per_capita": 4000,
                    "main_languages": ["Arabic", "Berber", "French"],
                    "key_sectors": ["Oil", "Gas", "Agriculture"],
                    "political_system": "Republic",
                    "independence_year": 1962
                }
            }

            # Try to load from file, fallback to defaults
            try:
                with open(self.countries_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    default_countries.update(file_data)
            except FileNotFoundError:
                logger.info(f"Country data file {self.countries_file} not found, using defaults")

            return default_countries

        except Exception as e:
            logger.warning(f"Error loading country data: {e}")
            return {}

    def get_country_vector(self, country: str) -> Optional[np.ndarray]:
        """Get vector representation for a country"""
        country_key = country.lower().replace(' ', '_')
        if country_key not in self.country_data:
            return None

        data = self.country_data[country_key]

        # Create a simple vector from country data
        vector = np.array([
            data.get("population", 0) / 1000000,  # Normalize population
            data.get("gdp_per_capita", 0) / 10000,  # Normalize GDP
            len(data.get("main_languages", [])),  # Number of languages
            len(data.get("key_sectors", [])),  # Number of sectors
            data.get("independence_year", 1900) / 2000,  # Normalize year
        ])

        # Normalize the vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def get_country_info(self, country: str) -> Optional[Dict]:
        """Get detailed information about a country"""
        country_key = country.lower().replace(' ', '_')
        return self.country_data.get(country_key)

    def get_similar_countries(self, country: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find countries similar to the given country"""
        target_vector = self.get_country_vector(country)
        if target_vector is None:
            return []

        similarities = []
        for country_name, data in self.country_data.items():
            if country_name != country.lower().replace(' ', '_'):
                other_vector = self.get_country_vector(country_name)
                if other_vector is not None:
                    similarity = np.dot(target_vector, other_vector)
                    similarities.append((country_name, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_countries_by_region(self, region: str) -> List[str]:
        """Get all countries in a specific region"""
        countries = []
        for country_key, data in self.country_data.items():
            if data.get("region", "").lower() == region.lower():
                countries.append(country_key)
        return countries

    def get_african_regions(self) -> List[str]:
        """Get all African regions"""
        regions = set()
        for data in self.country_data.values():
            region = data.get("region")
            if region:
                regions.add(region)
        return list(regions)

    def vectorize_query_with_country(self, query: str, country: Optional[str] = None) -> Dict:
        """Vectorize a query with country context"""
        result = {
            "query": query,
            "country": country,
            "country_vector": None,
            "country_info": None,
            "similar_countries": []
        }

        if country:
            result["country_vector"] = self.get_country_vector(country)
            result["country_info"] = self.get_country_info(country)
            result["similar_countries"] = self.get_similar_countries(country)

        return result

    def get_topic_country_relevance(self, topic: str, country: str) -> float:
        """Calculate relevance score between a topic and country"""
        country_info = self.get_country_info(country)
        if not country_info:
            return 0.0

        topic_lower = topic.lower()
        relevance_score = 0.0

        # Check sectors
        sectors = [s.lower() for s in country_info.get("key_sectors", [])]
        for sector in sectors:
            if sector in topic_lower:
                relevance_score += 0.5

        # Check languages
        languages = [l.lower() for l in country_info.get("main_languages", [])]
        for language in languages:
            if language in topic_lower:
                relevance_score += 0.3

        # Check region
        region = country_info.get("region", "").lower()
        if region in topic_lower:
            relevance_score += 0.4

        # Country name match
        if country.lower() in topic_lower:
            relevance_score += 1.0

        return min(relevance_score, 1.0)  # Cap at 1.0

if __name__ == "__main__":
    # Test the country vectorizer
    vectorizer = CountryVectorizer()

    print("Available countries:", list(vectorizer.country_data.keys()))
    print("\nTesting Nigeria:")
    nigeria_info = vectorizer.get_country_info("nigeria")
    print(json.dumps(nigeria_info, indent=2))

    print("\nSimilar countries to Nigeria:")
    similar = vectorizer.get_similar_countries("nigeria", 3)
    for country, score in similar:
        print(f"{country}: {score:.3f}")

    print("\nWest African countries:")
    west_africa = vectorizer.get_countries_by_region("West Africa")
    print(west_africa)
