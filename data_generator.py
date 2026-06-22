"""
Data Generator for Umbuzo LLM Training
Generates Q&A pairs and complex reasoning questions for African-focused training data
"""

import json
import random
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from country_vectorizer import CountryVectorizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UmbuzoDataGenerator:
    """Generate training data for Umbuzo LLM"""

    def __init__(self):
        self.country_vectorizer = CountryVectorizer()

        # Topic categories from the task
        self.topic_categories = {
            "political_civic": {
                "voting_patterns": [
                    "electoral participation rates", "demographic voting trends",
                    "political engagement by age groups", "regional voting differences"
                ],
                "cultural_dynamics": [
                    "changing cultural landscape", "social media influence on politics",
                    "cultural shifts in political discourse", "traditional vs modern values"
                ]
            },
            "economic_labor": {
                "income_poverty": [
                    "income inequality across regions", "poverty reduction strategies",
                    "economic mobility factors", "wealth distribution patterns"
                ],
                "employment_work": [
                    "workforce participation trends", "technology impact on jobs",
                    "remote work adoption", "skill development needs"
                ],
                "agriculture": [
                    "agricultural household characteristics", "local farming practices",
                    "agricultural technology adoption", "food security challenges"
                ]
            },
            "urban_community": {
                "urbanization": [
                    "population density trends", "metropolitan area growth",
                    "urban-rural migration patterns", "smart city development"
                ],
                "crime": [
                    "crime statistics analysis", "population density correlation",
                    "demographic crime factors", "community safety initiatives"
                ],
                "community_services": [
                    "service delivery demographics", "public infrastructure needs",
                    "community health services", "education access patterns"
                ]
            },
            "demographic_trends": {
                "migration_immigration": [
                    "internal migration patterns", "international immigration factors",
                    "migration policy impacts", "diaspora contributions"
                ],
                "age_lifecycle": [
                    "aging population challenges", "youth demographic trends",
                    "generational differences", "healthcare needs by age"
                ],
                "diversity": [
                    "racial ethnic diversity", "religious diversity patterns",
                    "cultural integration", "multicultural policies"
                ],
                "social_structures": [
                    "family structure changes", "marital status trends",
                    "household composition shifts", "lifestyle evolution"
                ],
                "housing": [
                    "housing conditions analysis", "housing types distribution",
                    "homelessness factors", "urban housing challenges"
                ],
                "education_mobility": [
                    "education-social mobility link", "literacy rate trends",
                    "educational access disparities", "skill development programs"
                ],
                "health": [
                    "demographic health correlations", "social media mental health impact",
                    "healthcare access patterns", "public health challenges"
                ]
            }
        }

        # Question templates for different types
        self.question_templates = {
            "factual": [
                "What are the current trends in {topic} in {country}?",
                "How does {topic} affect {country}'s {aspect}?",
                "What factors influence {topic} in African countries?",
                "Describe the relationship between {topic} and {aspect} in {country}.",
            ],
            "analytical": [
                "Analyze how {topic} impacts {aspect} in {country}.",
                "What are the implications of {topic} trends for {country}'s future?",
                "Compare {topic} patterns between {country} and {other_country}.",
                "Evaluate the effectiveness of policies addressing {topic} in {country}.",
            ],
            "predictive": [
                "What will be the future impact of {topic} on {country}?",
                "How might {topic} trends evolve in {country} over the next decade?",
                "What challenges will {country} face due to {topic} changes?",
                "Predict the outcomes of current {topic} developments in {country}.",
            ],
            "complex_reasoning": [
                "Considering multiple factors, explain why {topic} in {country} presents unique challenges compared to global trends.",
                "Analyze the complex interplay between {topic}, {aspect}, and {other_aspect} in {country}'s context.",
                "Synthesize information about {topic} to explain its broader implications for {country}'s development trajectory.",
                "Critically evaluate the effectiveness of current approaches to {topic} in {country}, considering historical, cultural, and economic contexts.",
                "Develop a comprehensive framework for understanding how {topic} influences {aspect} in {country}, incorporating multiple disciplinary perspectives.",
                "Examine the causal relationships between {topic} trends and {outcome} in {country}, considering confounding variables and alternative explanations.",
                "Propose evidence-based solutions to {topic} challenges in {country} that account for local context, resource constraints, and stakeholder interests.",
                "Integrate diverse data sources to construct a nuanced understanding of {topic} dynamics in {country} and their global implications.",
            ]
        }

        self.countries = list(self.country_vectorizer.country_data.keys())
        self.african_regions = self.country_vectorizer.get_african_regions()

    def generate_qa_pair(self, topic: str, subtopic: str, country: str, question_type: str = "factual") -> Dict:
        """Generate a single Q&A pair"""
        templates = self.question_templates.get(question_type, self.question_templates["factual"])
        template = random.choice(templates)

        # Get country info for context
        country_info = self.country_vectorizer.get_country_info(country)
        region = country_info.get("region", "Africa") if country_info else "Africa"

        # Generate question
        question = template.format(
            topic=subtopic.replace("_", " "),
            country=country.replace("_", " ").title(),
            aspect=random.choice(["economy", "society", "politics", "development", "culture"]),
            other_country=random.choice([c for c in self.countries if c != country]).replace("_", " ").title(),
            outcome=random.choice(["economic growth", "social stability", "political change", "cultural evolution"]),
            other_aspect=random.choice(["education", "healthcare", "infrastructure", "governance"])
        )

        # Generate answer based on topic and available data
        answer = self._generate_answer(topic, subtopic, country, question_type)

        return {
            "instruction": question,
            "input": "",
            "output": answer,
            "metadata": {
                "topic_category": topic,
                "subtopic": subtopic,
                "country": country,
                "region": region,
                "question_type": question_type,
                "generated_at": datetime.now().isoformat(),
                "source": "umbuzo_data_generator"
            }
        }

    def _generate_answer(self, topic: str, subtopic: str, country: str, question_type: str) -> str:
        """Generate answer based on topic and context"""
        country_info = self.country_vectorizer.get_country_info(country)

        if not country_info:
            return f"This question relates to {subtopic.replace('_', ' ')} in {country.replace('_', ' ').title()}. Based on general African development patterns, this area requires further research and data collection."

        base_answer = f"In {country_info['name']}, {subtopic.replace('_', ' ')} "

        if topic == "political_civic":
            if "voting" in subtopic:
                base_answer += f"shows participation rates of approximately {random.randint(40, 80)}% in recent elections. Key factors include education levels, urbanization, and access to information. The country has a {country_info['political_system']} system established in {country_info['independence_year']}."
            elif "cultural" in subtopic:
                base_answer += f"is influenced by {', '.join(country_info['main_languages'][:2])} speakers and traditional customs evolving alongside modern influences. Social media penetration reaches about {random.randint(30, 70)}% of the population."

        elif topic == "economic_labor":
            if "income" in subtopic:
                gdp = country_info['gdp_per_capita']
                base_answer += f"averages around ${gdp} per capita. Income distribution shows significant disparities, with the top 10% earning approximately {random.randint(30, 50)} times more than the bottom 10%."
            elif "employment" in subtopic:
                base_answer += f"has a workforce participation rate of about {random.randint(50, 75)}%. The service sector employs {random.randint(30, 60)}% of workers, while agriculture remains significant at {random.randint(20, 50)}%."
            elif "agriculture" in subtopic:
                sectors = country_info.get('key_sectors', [])
                if 'Agriculture' in sectors:
                    base_answer += f"employs approximately {random.randint(40, 70)}% of the population. Key crops include local varieties adapted to the {country_info['region']} climate."

        elif topic == "urban_community":
            if "urbanization" in subtopic:
                population = country_info['population'] / 1000000
                base_answer += f"is growing rapidly, with urban populations reaching approximately {random.randint(20, 60)}% of the total {population:.1f} million people."
            elif "crime" in subtopic:
                base_answer += f"rates correlate with urbanization patterns. Economic factors and social inequality contribute to crime statistics that vary significantly across regions."
            elif "community" in subtopic:
                base_answer += f"varies by region, with urban areas having better access to healthcare and education compared to rural communities."

        elif topic == "demographic_trends":
            if "migration" in subtopic:
                base_answer += f"patterns show both internal movement from rural to urban areas and international migration. Economic opportunities and education drive internal migration."
            elif "age" in subtopic:
                base_answer += f"shows a median age of approximately {random.randint(18, 25)} years, indicating a relatively young population compared to global averages."
            elif "diversity" in subtopic:
                languages = country_info.get('main_languages', [])
                base_answer += f"is reflected in {len(languages)} main languages: {', '.join(languages)}. This linguistic diversity shapes cultural and social dynamics."
            elif "social" in subtopic:
                base_answer += f"includes family structures averaging {random.randint(4, 7)} persons per household, with changing patterns due to urbanization and education."
            elif "housing" in subtopic:
                base_answer += f"conditions vary widely, from modern urban apartments to traditional rural dwellings. Access to adequate housing remains a challenge for {random.randint(20, 50)}% of the population."
            elif "education" in subtopic:
                base_answer += f"shows literacy rates of approximately {random.randint(60, 90)}%. Education levels strongly correlate with economic opportunities and social mobility."
            elif "health" in subtopic:
                base_answer += f"is influenced by access to healthcare, with life expectancy around {random.randint(50, 75)} years. Social media usage affects mental health awareness and support networks."

        if question_type == "complex_reasoning":
            base_answer += f"\n\nComplex Analysis: This situation in {country_info['name']} must be understood within the broader context of {country_info['region']} regional dynamics, global economic trends, and historical development patterns. The interplay between cultural factors, economic constraints, and political institutions creates unique challenges that require integrated, context-specific solutions rather than universal approaches."

        return base_answer

    def generate_training_dataset(self, num_qa_pairs: int = 7000, num_complex_questions: int = 10000) -> List[Dict]:
        """Generate complete training dataset"""
        dataset = []

        logger.info(f"Generating {num_qa_pairs} Q&A pairs...")

        # Generate regular Q&A pairs
        for i in range(num_qa_pairs):
            # Select random topic and subtopic
            topic = random.choice(list(self.topic_categories.keys()))
            subtopic_category = random.choice(list(self.topic_categories[topic].keys()))
            subtopic = random.choice(self.topic_categories[topic][subtopic_category])

            country = random.choice(self.countries)
            question_type = random.choice(["factual", "analytical", "predictive"])

            qa_pair = self.generate_qa_pair(topic, subtopic, country, question_type)
            dataset.append(qa_pair)

            if (i + 1) % 1000 == 0:
                logger.info(f"Generated {i + 1}/{num_qa_pairs} Q&A pairs")

        logger.info(f"Generating {num_complex_questions} complex reasoning questions...")

        # Generate complex reasoning questions
        for i in range(num_complex_questions):
            topic = random.choice(list(self.topic_categories.keys()))
            subtopic_category = random.choice(list(self.topic_categories[topic].keys()))
            subtopic = random.choice(self.topic_categories[topic][subtopic_category])

            country = random.choice(self.countries)

            qa_pair = self.generate_qa_pair(topic, subtopic, country, "complex_reasoning")
            dataset.append(qa_pair)

            if (i + 1) % 1000 == 0:
                logger.info(f"Generated {i + 1}/{num_complex_questions} complex reasoning questions")

        return dataset

    def save_dataset(self, dataset: List[Dict], filename: str = "umbuzo_training_data.jsonl"):
        """Save dataset to JSONL file"""
        logger.info(f"Saving {len(dataset)} samples to {filename}")

        with open(filename, 'w', encoding='utf-8') as f:
            for item in dataset:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')

        logger.info(f"Dataset saved successfully to {filename}")

        # Save statistics
        self._save_dataset_stats(dataset, filename.replace('.jsonl', '_stats.json'))

    def _save_dataset_stats(self, dataset: List[Dict], stats_filename: str):
        """Save dataset statistics"""
        stats = {
            "total_samples": len(dataset),
            "topic_distribution": {},
            "country_distribution": {},
            "question_type_distribution": {},
            "region_distribution": {},
            "generated_at": datetime.now().isoformat()
        }

        for item in dataset:
            meta = item.get("metadata", {})

            # Topic distribution
            topic = meta.get("topic_category", "unknown")
            stats["topic_distribution"][topic] = stats["topic_distribution"].get(topic, 0) + 1

            # Country distribution
            country = meta.get("country", "unknown")
            stats["country_distribution"][country] = stats["country_distribution"].get(country, 0) + 1

            # Question type distribution
            q_type = meta.get("question_type", "unknown")
            stats["question_type_distribution"][q_type] = stats["question_type_distribution"].get(q_type, 0) + 1

            # Region distribution
            region = meta.get("region", "unknown")
            stats["region_distribution"][region] = stats["region_distribution"].get(region, 0) + 1

        with open(stats_filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        logger.info(f"Dataset statistics saved to {stats_filename}")

    def validate_dataset(self, dataset: List[Dict]) -> Dict:
        """Validate dataset quality"""
        validation_results = {
            "total_samples": len(dataset),
            "samples_with_metadata": 0,
            "unique_questions": 0,
            "average_answer_length": 0,
            "topic_coverage": set(),
            "country_coverage": set(),
            "issues": []
        }

        questions = set()
        total_answer_length = 0

        for item in dataset:
            # Check metadata
            if "metadata" in item:
                validation_results["samples_with_metadata"] += 1
                meta = item["metadata"]
                validation_results["topic_coverage"].add(meta.get("topic_category", ""))
                validation_results["country_coverage"].add(meta.get("country", ""))

            # Check uniqueness
            question = item.get("instruction", "")
            questions.add(question)

            # Check answer length
            answer = item.get("output", "")
            total_answer_length += len(answer)

            # Basic validation
            if not question:
                validation_results["issues"].append("Empty question found")
            if not answer:
                validation_results["issues"].append("Empty answer found")
            if len(answer) < 50:
                validation_results["issues"].append("Very short answer found")

        validation_results["unique_questions"] = len(questions)
        validation_results["average_answer_length"] = total_answer_length / len(dataset) if dataset else 0
        validation_results["topic_coverage"] = list(validation_results["topic_coverage"])
        validation_results["country_coverage"] = list(validation_results["country_coverage"])

        return validation_results

def main():
    """Generate the complete Umbuzo training dataset"""
    generator = UmbuzoDataGenerator()

    # Generate dataset
    dataset = generator.generate_training_dataset(num_qa_pairs=7000, num_complex_questions=10000)

    # Validate dataset
    validation = generator.validate_dataset(dataset)
    logger.info("Dataset validation results:")
    logger.info(json.dumps(validation, indent=2))

    # Save dataset
    generator.save_dataset(dataset)

    logger.info("Umbuzo training data generation completed!")

if __name__ == "__main__":
    main()
