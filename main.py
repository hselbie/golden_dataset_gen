import os
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Tuple, Union, Optional

import pandas as pd

import ExampleQueries
from config.variable_config import VarConfig
from config.component_factory import (
    create_query_analyzer,
    create_query_generator,
    create_answer_generator,
    create_query_components,
)
from querygenerator.generator import QueryGenerator, AnswerGenerator, QueryAnalyzer


class AnswerSource(Enum):
    """Available sources for generating answers."""

    LLM = "llm"
    DATASTORE = "datastore"
    SEARCH = "google"
    ALL = "all"
    NONE = "none"


class OutputFormat(Enum):
    """Output format options for results."""

    TEXT = "text"
    DATAFRAME = "dataframe"
    BOTH = "both"


@dataclass
class QueryConfig:
    """Configuration for query processing."""

    num_questions: int = 3
    answer_source: AnswerSource = AnswerSource.LLM
    generate_answers: bool = True


# Create output directory if it doesn't exist
os.makedirs("generated_datasets", exist_ok=True)

global_variables = VarConfig()


def generate_domain_dataset(
    queries: List[Tuple[str, str]], domain_name: str, num_questions: int = 15
) -> pd.DataFrame:
    """
    Generate dataset for a specific domain.

    Args:
        queries: List of (query, query_id) tuples
        domain_name: Name of the domain for categorization
        num_questions: Number of questions to generate per query

    Returns:
        DataFrame containing generated questions and answers
    """
    dataset = []
    analyzer = create_query_analyzer()
    generator = create_query_generator(config=global_variables)

    for query, query_id in queries:
        # Extract elements and generate questions
        elements = analyzer.extract_elements(query)
        questions = generator.generate_questions(elements, num_questions=num_questions)

        # Generate answers using different sources
        # qa_pairs_datastore = analyzer.generate_answers(questions, source="datastore")
        qa_pairs_google = generator.generate_answers(questions, source="google")
        qa_pairs_llm = generator.generate_answers(questions, source="llm")

        # Combine results
        for (q, a_gs), (_, a_llm) in zip(qa_pairs_google, qa_pairs_llm):
            dataset.append(
                {
                    "query_id": query_id,
                    "original_query": query,
                    "generated_question": q,
                    "google_search_answer": a_gs,
                    "llm_answer": a_llm,
                    "domain": domain_name,
                }
            )

    return pd.DataFrame(dataset)


def process_queries(queries: List[Tuple[str, str]], qconfig: QueryConfig) -> List[Dict]:
    """
    Process multiple queries with configurable options.

    Args:
        queries: List of (query, query_id) tuples to process
        qconfig: QueryConfig object with processing parameters

    Returns:
        List of dictionaries containing query results
    """
    # Create all components using factory - this eliminates duplication
    _, _, query_analyzer, query_generator, answer_generator = create_query_components(
        config=global_variables
    )

    results = []

    for query, query_id in queries:
        print(f"\nProcessing query: {query}")

        # Extract elements
        elements = query_analyzer.extract_elements(query)

        # Generate questions
        questions = query_generator.generate_questions(
            elements, num_questions=qconfig.num_questions
        )

        result = {
            "query_id": query_id,
            "original_query": query,
            "generated_questions": questions,
            "qa_pairs": [],
        }

        # Generate answers if requested
        if qconfig.generate_answers:
            if qconfig.answer_source == AnswerSource.ALL:
                # Generate answers from all sources
                qa_pairs_llm = answer_generator.generate_answers(
                    questions, source="llm"
                )
                qa_pairs_ds = answer_generator.generate_answers(
                    questions, source="datastore"
                )
                qa_pairs_search = answer_generator.generate_answers(
                    questions, source="google"
                )

                result["qa_pairs"] = {
                    "llm": qa_pairs_llm,
                    "datastore": qa_pairs_ds,
                    "search": qa_pairs_search,
                }
            else:
                # Generate answers from specific source
                qa_pairs = answer_generator.generate_answers(
                    questions, source=qconfig.answer_source.value
                )
                result["qa_pairs"] = {qconfig.answer_source.value: qa_pairs}

        results.append(result)

    return results


def main(
    queries: List[Tuple[str, str]],
    config: QueryConfig,
    output_format: OutputFormat = OutputFormat.BOTH,
    save_csv: bool = True,
) -> Union[pd.DataFrame, None]:
    """
    Process queries with given configuration and return results in specified format

    Args:
        queries: List of (query, query_id) tuples
        config: QueryConfig object with processing parameters
        output_format: OutputFormat enum specifying desired output format
        save_csv: Whether to save results to CSV file

    Returns:
        pd.DataFrame if output_format is DATAFRAME or BOTH, None otherwise
    """
    results = process_queries(queries, config)

    # Text output handling
    if output_format in [OutputFormat.TEXT, OutputFormat.BOTH]:
        for result in results:
            print(
                f"\nOriginal Query ({result['query_id']}): {result['original_query']}"
            )
            print("-" * 50)
            print("\nGenerated Questions:")
            for q in result["generated_questions"]:
                print(f"- {q}")

            if result["qa_pairs"]:
                print("\nAnswers:")
                for source, qa_pairs in result["qa_pairs"].items():
                    print(f"\n{source.upper()} Answers:")
                    for q, a in qa_pairs:
                        print(f"Q: {q}")
                        print(f"A: {a}\n")

    # DataFrame output
    if output_format in [OutputFormat.DATAFRAME, OutputFormat.BOTH]:
        # Initialize list to store all unique answer sources
        answer_sources = set()
        rows = []

        # First pass: collect all possible answer sources
        for result in results:
            if result["qa_pairs"]:
                answer_sources.update(result["qa_pairs"].keys())

        # Second pass: create rows with dynamic columns
        for result in results:
            for q in result["generated_questions"]:
                # Base row with question info
                row = {
                    "query_id": result["query_id"],
                    "original_query": result["original_query"],
                    "generated_question": q,
                }

                # Initialize all possible answer columns as None
                for source in answer_sources:
                    row[f"{source}_answer"] = None

                # Fill in available answers
                if result["qa_pairs"]:
                    for source, qa_pairs in result["qa_pairs"].items():
                        for quest, ans in qa_pairs:
                            if quest == q:
                                row[f"{source}_answer"] = ans

                rows.append(row)

        df = pd.DataFrame(rows)

        # Reorder columns to group related information
        base_cols = ["query_id", "original_query", "generated_question"]
        answer_cols = [col for col in df.columns if col.endswith("_answer")]
        df = df[base_cols + sorted(answer_cols)]

        if save_csv:
            output_path = "generated_datasets/query_results.csv"
            df.to_csv(output_path, index=False)
            print(f"\nResults saved to {output_path}")

            # Print summary of available answer sources
            print("\nAnswer sources in dataset:")
            for source in sorted(answer_sources):
                print(f"- {source}")

        return df

    return None


if __name__ == "__main__":
    # Example queries
    sample_queries = [
        ("What are popular attractions in Seattle?", "q1"),
        ("What restaurants serve vegan food in Austin?", "q2"),
        ("What would be a good teambuilding outdoor activity in Manhattan?", "q3"),
    ]

    # Example configurations
    questions_only = QueryConfig(num_questions=5, generate_answers=False)

    # Example usage with different output formats
    # Text output only
    # main(sample_queries, questions_only, output_format=OutputFormat.TEXT)

    # DataFrame output only
    df = main(sample_queries, questions_only, output_format=OutputFormat.DATAFRAME)
    print(df.head())
    print(df.describe())

    # Both outputs
    # df = main(sample_queries, questions_only, output_format=OutputFormat.BOTH)
