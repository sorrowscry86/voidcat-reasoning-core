# rag_engine.py
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

KNOWLEDGE_BASE_DIR = "knowledge_source"

class RagEngine:
    def __init__(self):
        self.documents = []
        self.vectorizer = TfidfVectorizer()
        self.doc_vectors = None
        self._load_documents()

    def _load_documents(self):
        """Loads all documents from the knowledge base directory."""
        print("Loading knowledge base...")
        for filename in os.listdir(KNOWLEDGE_BASE_DIR):
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            if os.path.isfile(filepath) and filename.endswith('.md'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.documents.append(f.read())

        if self.documents:
            self.doc_vectors = self.vectorizer.fit_transform(self.documents)
            print(f"Successfully loaded and vectorized {len(self.documents)} document(s).")
        else:
            print("Warning: No documents found in knowledge base.")

    def retrieve_context(self, query: str, top_k: int = 1) -> str:
        """Retrieves the most relevant document chunk for a given query."""
        if self.doc_vectors is None or not self.documents:
            return "No knowledge base loaded."

        query_vector = self.vectorizer.transform([query])
        cosine_similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()

        # Get the indices of the top_k most similar documents
        # We use argpartition for efficiency if top_k is small
        if top_k >= len(self.documents):
            relevant_doc_indices = cosine_similarities.argsort()[::-1]
        else:
            relevant_doc_indices = np.argpartition(cosine_similarities, -top_k)[-top_k:]
            relevant_doc_indices = relevant_doc_indices[np.argsort(cosine_similarities[relevant_doc_indices])][::-1]

        return "\n---\n".join([self.documents[i] for i in relevant_doc_indices])

# This allows the engine to be initialized when the module is imported.
engine = RagEngine()

def get_relevant_context(query: str) -> str:
    """A simple interface to the RAG engine's retrieval function."""
    return engine.retrieve_context(query)

