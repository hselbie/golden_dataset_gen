from config.variable_config import VarConfig
from config.component_factory import create_llm
import pandas as pd
import json
import os
import random
import logging
from google.cloud import storage

logger = logging.getLogger(__name__)


class QueryDatasetGenerator:
    """
    Generates a dataset of questions and answers from documents for RAG evaluation.
    Supports loading documents from GCS buckets.
    """

    def __init__(self):
        """Initialize the generator with necessary components"""
        # Load configuration
        self.config = VarConfig()

        # Initialize language model using factory - eliminates duplication
        self.llm = create_llm(config=self.config)

        # Initialize GCS client
        self.storage_client = storage.Client()

        # Ensure output directory exists
        os.makedirs("generated_datasets", exist_ok=True)

    def load_document_from_gcs(self, bucket_name, blob_name):
        """
        Load a document from a GCS bucket

        Args:
            bucket_name: Name of the GCS bucket
            blob_name: Name of the blob/file to load

        Returns:
            Document dictionary with text and metadata
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download as string
        content = blob.download_as_text()

        # Create document dictionary
        document = {
            "text": content,
            "source": f"gs://{bucket_name}/{blob_name}",
            "doc_id": blob_name,
        }

        return document

    def load_documents_from_gcs_folder(self, bucket_name, prefix=""):
        """
        Load all documents from a GCS bucket folder

        Args:
            bucket_name: Name of the GCS bucket
            prefix: Optional prefix (folder path) to filter by

        Returns:
            List of document dictionaries
        """
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)

        documents = []
        for blob in blobs:
            # Skip folders or other non-text files
            if blob.name.endswith("/") or not self._is_text_file(blob.name):
                continue

            try:
                content = blob.download_as_text()
                documents.append(
                    {
                        "text": content,
                        "source": f"gs://{bucket_name}/{blob.name}",
                        "doc_id": blob.name,
                    }
                )
            except Exception as e:
                logger.error(f"Error loading {blob.name}: {e}")

        return documents

    def _is_text_file(self, filename):
        """Check if a file is likely to be text-based"""
        text_extensions = [
            ".txt",
            ".md",
            ".json",
            ".csv",
            ".py",
            ".js",
            ".html",
            ".xml",
            ".log",
            ".yml",
            ".yaml",
        ]
        return any(filename.lower().endswith(ext) for ext in text_extensions)

    def chunk_document(self, document, chunk_size=3000, overlap=1000):
        """
        Split a document into overlapping chunks for processing

        Args:
            document: Document dictionary or text string
            chunk_size: Maximum size of each chunk
            overlap: Overlap between consecutive chunks

        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Extract document text and source
        if isinstance(document, dict):
            text = document.get("text", "")
            source = document.get("source", "unknown")
            doc_id = document.get("doc_id", 0)
        else:
            text = document
            source = "unknown"
            doc_id = 0

        chunks = []

        # Create chunks with overlap
        stride = chunk_size - overlap
        for i in range(0, len(text), stride):
            chunk_text = text[i : i + chunk_size]
            if len(chunk_text) < 200:  # Skip small chunks
                continue

            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        "source": source,
                        "doc_id": doc_id,
                        "start_pos": i,
                        "end_pos": i + len(chunk_text),
                    },
                }
            )

        return chunks

    def generate_qa_pairs(self, chunk, num_questions=5):
        """
        Generate question-answer pairs from a document chunk

        Args:
            chunk: Document chunk dictionary
            num_questions: Number of QA pairs to generate

        Returns:
            List of QA pair dictionaries
        """
        prompt = f"""
        Based on the following text, generate {num_questions} diverse and natural question-answer pairs.
        
        TEXT:
        {chunk["text"]}
        
        Generate questions that:
        1. Have answers fully supported by the text
        2. Vary in difficulty and complexity
        3. Cover different aspects of the content
        
        For each pair, the answer should be accurate and concise.
        
        Format your response as a JSON array with objects containing "question" and "answer" fields.
        """

        response = self.llm.invoke(prompt)

        qa_pairs = []
        try:
            content = response.content
            # Extract JSON from response
            start_idx = content.find("[")
            end_idx = content.rfind("]") + 1

            if start_idx >= 0 and end_idx > 0:
                json_str = content[start_idx:end_idx]
                chunk_qa_pairs = json.loads(json_str)

                # Add source metadata to each pair
                for qa in chunk_qa_pairs:
                    qa["source"] = chunk["metadata"]["source"]
                    qa["doc_id"] = chunk["metadata"]["doc_id"]
                    qa_pairs.append(qa)

        except Exception as e:
            logger.error(f"Error generating QA pairs: {e}")

        return qa_pairs

    def generate_dataset_from_documents(self, documents, total_questions=100):
        """
        Generate a complete QA dataset from multiple documents

        Args:
            documents: List of document dictionaries or strings
            total_questions: Total number of questions to generate

        Returns:
            DataFrame with generated QA pairs
        """
        all_chunks = []

        # Process each document into chunks
        for doc_idx, doc in enumerate(documents):
            if isinstance(doc, str):
                doc = {"text": doc, "source": f"document_{doc_idx}", "doc_id": doc_idx}

            doc_chunks = self.chunk_document(doc)
            all_chunks.extend(doc_chunks)

        # Calculate questions per chunk
        num_chunks = len(all_chunks)
        if num_chunks == 0:
            logger.warning("No valid chunks found in documents")
            return pd.DataFrame()

        questions_per_chunk = max(1, total_questions // num_chunks)

        # Generate QA pairs for each chunk
        all_qa_pairs = []
        for chunk in all_chunks:
            qa_pairs = self.generate_qa_pairs(chunk, questions_per_chunk)
            all_qa_pairs.extend(qa_pairs)

            logger.info(
                f"Generated {len(qa_pairs)} QA pairs from chunk in {chunk['metadata']['source']}"
            )

        # Convert to DataFrame and save
        qa_df = pd.DataFrame(all_qa_pairs)
        qa_df.to_csv("generated_datasets/golden_qa_dataset.csv", index=False)

        logger.info(
            f"Created dataset with {len(qa_df)} question-answer pairs for evaluation"
        )
        return qa_df

    def generate_dataset_from_gcs(self, bucket_name, prefix="", total_questions=100):
        """
        Generate a golden dataset from documents in a GCS bucket

        Args:
            bucket_name: Name of the GCS bucket
            prefix: Optional prefix/folder to filter by
            total_questions: Total number of questions to generate

        Returns:
            DataFrame with generated QA pairs
        """
        # Load documents from GCS
        logger.info(f"Loading documents from gs://{bucket_name}/{prefix}...")
        documents = self.load_documents_from_gcs_folder(bucket_name, prefix)

        logger.info(f"Loaded {len(documents)} documents from GCS")

        # Generate dataset from loaded documents
        return self.generate_dataset_from_documents(documents, total_questions)

    def save_dataset_to_gcs(self, df, bucket_name, blob_name="golden_qa_dataset.csv"):
        """
        Save the generated dataset to a GCS bucket

        Args:
            df: DataFrame with QA pairs
            bucket_name: Name of the GCS bucket
            blob_name: Name of the file to create

        Returns:
            GCS URI of the saved file
        """
        # Save to local file first
        local_path = "generated_datasets/golden_qa_dataset.csv"
        df.to_csv(local_path, index=False)

        # Upload to GCS
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(local_path)

        gcs_uri = f"gs://{bucket_name}/{blob_name}"
        logger.info(f"Dataset saved to {gcs_uri}")

        return gcs_uri
