# context7_integration.py
"""
VoidCat Context7 Integration Module

Provides intelligent context retrieval and enhancement capabilities using
Context7-style patterns for improved reasoning accuracy and relevance.

This module implements:
- Multi-source context aggregation
- Relevance scoring and ranking
- Context coherence analysis
- Adaptive context selection
- Integration with sequential thinking

Author: VoidCat Reasoning Core Team
License: MIT
Version: 1.0.0
"""

import asyncio
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def debug_print(message: str) -> None:
    """Print debug messages to stderr to avoid interfering with MCP protocol."""
    print(f"[Context7] {message}", file=sys.stderr, flush=True)


@dataclass
class ContextSource:
    """Represents a source of contextual information."""

    id: str
    name: str
    type: str  # 'document', 'knowledge_base', 'external_api', etc.
    content: str
    metadata: Dict[str, Any]
    relevance_score: float = 0.0
    last_accessed: str = ""

    def __post_init__(self):
        if not self.last_accessed:
            self.last_accessed = datetime.now(UTC).isoformat()


@dataclass
class ContextCluster:
    """Represents a cluster of related context sources."""

    id: str
    theme: str
    sources: List[ContextSource]
    coherence_score: float
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


@dataclass
class ContextRequest:
    """Request for context retrieval and analysis."""

    id: str
    query: str
    domain: Optional[str] = None
    max_sources: int = 5
    min_relevance: float = 0.3
    relevance_threshold: float = 0.3  # Added for compatibility
    strategy: str = "similarity"  # Added for compatibility
    include_metadata: bool = True
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        # Ensure compatibility
        if not hasattr(self, "relevance_threshold"):
            self.relevance_threshold = self.min_relevance
        if not hasattr(self, "strategy"):
            self.strategy = "similarity"


@dataclass
class ContextResponse:
    """Response containing retrieved context sources."""

    request_id: str
    sources: List[ContextSource]
    relevance_scores: Dict[str, float]
    clusters_used: List[str]
    processing_metadata: Dict[str, Any]
    retrieved_at: str = ""

    def __post_init__(self):
        if not self.retrieved_at:
            self.retrieved_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ContextResponse to a dictionary representation.
        """
        return {
            "request_id": self.request_id,
            "sources": [asdict(source) for source in self.sources],
            "relevance_scores": self.relevance_scores,
            "clusters_used": self.clusters_used,
            "processing_metadata": self.processing_metadata,
            "retrieved_at": self.retrieved_at,
        }

    def dict(self) -> Dict[str, Any]:
        """
        Alias for to_dict to ensure compatibility.
        """
        return self.to_dict()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an attribute value by key, with a default fallback.
        """
        return getattr(self, key, default)


class Context7Engine:
    """
    Advanced context retrieval and analysis engine inspired by Context7 patterns.

    Provides intelligent context aggregation, relevance scoring, and coherence
    analysis to enhance reasoning capabilities with high-quality contextual information.

    Key Features:
    - Multi-source context aggregation
    - Advanced relevance scoring using TF-IDF and semantic similarity
    - Context coherence analysis and clustering
    - Adaptive context selection based on query complexity
    - Integration with sequential thinking workflows
    """

    def __init__(self, knowledge_dirs: Optional[List[str]] = None):
        """
        Initialize the Context7 engine.

        Args:
            knowledge_dirs: List of directories containing knowledge sources
        """
        self.knowledge_dirs = knowledge_dirs or ["knowledge_source"]
        self.context_sources: Dict[str, ContextSource] = {}
        self.context_clusters: Dict[str, ContextCluster] = {}
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words="english",
            lowercase=True,
            ngram_range=(1, 2),  # Use bigrams for better context
            min_df=1,
            max_df=1.0,  # Allow all document frequencies for small datasets
        )
        self.source_vectors = None
        self.requests_processed = 0
        self._initialization_task = None
        self._initialized = False

        # Schedule initialization but don't create task immediately
        # Will be initialized on first use

        debug_print("Context7 Engine initialized")

    async def _initialize_context_sources(self) -> None:
        """Initialize and load context sources from configured directories."""
        debug_print("Initializing context sources...")

        total_sources = 0

        for knowledge_dir in self.knowledge_dirs:
            # Ensure knowledge_dir is absolute path
            if not os.path.isabs(knowledge_dir):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                knowledge_dir = os.path.join(script_dir, knowledge_dir)

            if not os.path.isdir(knowledge_dir):
                debug_print(f"Warning: Knowledge directory '{knowledge_dir}' not found")
                continue

            # Load markdown files
            markdown_files = list(Path(knowledge_dir).rglob("*.md"))
            for file_path in markdown_files:
                try:
                    source = await self._load_document_source(file_path)
                    if source:
                        self.context_sources[source.id] = source
                        total_sources += 1
                        debug_print(f"  ✓ Loaded context source: {source.name}")
                except Exception as e:
                    debug_print(f"  ✗ Failed to load {file_path}: {str(e)}")

        if self.context_sources:
            await self._build_source_vectors()
            await self._analyze_context_clusters()
            debug_print(
                f"Context7 initialization complete: {total_sources} sources loaded"
            )
        else:
            debug_print("Warning: No context sources loaded")

    async def _load_document_source(self, file_path: Path) -> Optional[ContextSource]:
        """
        Load a document as a context source.

        Args:
            file_path: Path to the document file

        Returns:
            ContextSource object or None if loading fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                return None

            # Extract metadata from content
            metadata = self._extract_document_metadata(content, file_path)

            source = ContextSource(
                id=f"doc_{file_path.stem}_{hash(str(file_path)) % 10000}",
                name=file_path.name,
                type="document",
                content=content,
                metadata=metadata,
            )

            return source

        except Exception as e:
            debug_print(f"Error loading document {file_path}: {str(e)}")
            return None

    def _extract_document_metadata(
        self, content: str, file_path: Path
    ) -> Dict[str, Any]:
        """
        Extract metadata from document content.

        Args:
            content: Document content
            file_path: Path to the document

        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            "file_path": str(file_path),
            "file_size": len(content),
            "word_count": len(content.split()),
            "line_count": len(content.splitlines()),
            "created_at": datetime.now(UTC).isoformat(),
        }

        # Extract title from first header or filename
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        metadata["title"] = title_match.group(1) if title_match else file_path.stem

        # Extract tags from content
        tag_pattern = r"(?:#|tags?:)\s*([^\n]+)"
        tag_matches = re.findall(tag_pattern, content, re.IGNORECASE)
        if tag_matches:
            tags = []
            for match in tag_matches:
                tags.extend(
                    [tag.strip() for tag in re.split(r"[,\s]+", match) if tag.strip()]
                )
            metadata["tags"] = list(set(tags))

        # Extract section headers
        headers = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
        metadata["sections"] = headers[:10]  # Limit to first 10 headers

        # Identify key topics using simple keyword extraction
        keywords = self._extract_keywords(content)
        metadata["keywords"] = keywords[:20]  # Top 20 keywords

        return metadata

    def _extract_keywords(self, content: str) -> List[str]:
        """
        Extract key terms from content using simple frequency analysis.

        Args:
            content: Document content

        Returns:
            List of extracted keywords
        """
        # Simple keyword extraction
        words = re.findall(r"\b[a-zA-Z]{3,}\b", content.lower())

        # Remove common words
        stop_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "man",
            "new",
            "now",
            "old",
            "see",
            "two",
            "way",
            "who",
            "boy",
            "did",
            "its",
            "let",
            "put",
            "say",
            "she",
            "too",
            "use",
            "that",
            "with",
        }

        filtered_words = [
            word for word in words if word not in stop_words and len(word) > 3
        ]

        # Count frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Return top words by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words if freq > 1][:20]

    async def _build_source_vectors(self) -> None:
        """Build TF-IDF vectors for all context sources."""
        if not self.context_sources:
            return

        documents = [source.content for source in self.context_sources.values()]

        try:
            self.source_vectors = self.vectorizer.fit_transform(documents)
            debug_print(
                f"Built vectors for {len(documents)} sources with {self.source_vectors.shape[1]} features"
            )
        except Exception as e:
            debug_print(f"Error building source vectors: {str(e)}")
            self.source_vectors = None

    async def _analyze_context_clusters(self) -> None:
        """Analyze and create context clusters based on semantic similarity."""
        if self.source_vectors is None or self.source_vectors.shape[0] == 0:
            return

        try:
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(self.source_vectors)

            # Simple clustering based on high similarity threshold
            similarity_threshold = 0.3
            processed_sources = set()
            cluster_id = 0

            source_list = list(self.context_sources.values())

            for i, source in enumerate(source_list):
                if source.id in processed_sources:
                    continue

                # Find similar sources
                similar_indices = np.where(similarity_matrix[i] > similarity_threshold)[
                    0
                ]
                similar_sources = [
                    source_list[j]
                    for j in similar_indices
                    if source_list[j].id not in processed_sources
                ]

                if len(similar_sources) > 1:
                    # Create cluster
                    cluster = ContextCluster(
                        id=f"cluster_{cluster_id}",
                        theme=self._generate_cluster_theme(similar_sources),
                        sources=similar_sources,
                        coherence_score=np.mean(similarity_matrix[i][similar_indices]),
                    )

                    self.context_clusters[cluster.id] = cluster

                    # Mark sources as processed
                    for sim_source in similar_sources:
                        processed_sources.add(sim_source.id)

                    cluster_id += 1

            debug_print(f"Created {len(self.context_clusters)} context clusters")

        except Exception as e:
            debug_print(f"Error analyzing context clusters: {str(e)}")

    def _generate_cluster_theme(self, sources: List[ContextSource]) -> str:
        """
        Generate a theme name for a cluster of sources.

        Args:
            sources: List of sources in the cluster

        Returns:
            Generated theme name
        """
        # Collect all keywords from sources
        all_keywords = []
        for source in sources:
            keywords = source.metadata.get("keywords", [])
            all_keywords.extend(keywords)

        if not all_keywords:
            return f"Document Cluster ({len(sources)} sources)"

        # Find most common keywords
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1

        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [kw for kw, freq in sorted_keywords[:3]]

        if top_keywords:
            return f"{' & '.join(top_keywords).title()}"
        else:
            return f"Document Cluster ({len(sources)} sources)"

    async def retrieve_context(self, request: ContextRequest) -> ContextResponse:
        """
        Retrieve relevant context based on a context request.

        Args:
            request: ContextRequest object with query and parameters

        Returns:
            ContextResponse with relevant context sources
        """
        try:
            # Ensure proper initialization
            await self.ensure_initialized()

            if not self.context_sources:
                return ContextResponse(
                    request_id=request.id,
                    sources=[],
                    relevance_scores={},
                    clusters_used=[],
                    processing_metadata={"error": "No context sources available"},
                )

            # Get relevance scores for all sources
            relevance_scores = {}
            for source_id, source in self.context_sources.items():
                score = await self._calculate_relevance_score(request.query, source)
                relevance_scores[source_id] = score

            # Sort sources by relevance
            sorted_sources = sorted(
                relevance_scores.items(), key=lambda x: x[1], reverse=True
            )

            # Select top sources based on max_sources
            selected_sources = []
            for source_id, score in sorted_sources[: request.max_sources]:
                if score >= request.relevance_threshold:
                    selected_sources.append(self.context_sources[source_id])

            # Identify clusters used
            clusters_used = []
            for cluster_id, cluster in self.context_clusters.items():
                cluster_sources = {s.id for s in cluster.sources}
                selected_source_ids = {s.id for s in selected_sources}
                if cluster_sources.intersection(selected_source_ids):
                    clusters_used.append(cluster_id)

            # Create processing metadata
            processing_metadata = {
                "total_sources_evaluated": len(self.context_sources),
                "sources_above_threshold": len(selected_sources),
                "max_relevance_score": (
                    max(relevance_scores.values()) if relevance_scores else 0
                ),
                "clusters_analyzed": len(self.context_clusters),
                "processing_strategy": request.strategy,
            }

            debug_print(
                f"Context retrieval: {len(selected_sources)} sources selected from {len(self.context_sources)} available"
            )

            return ContextResponse(
                request_id=request.id,
                sources=selected_sources,
                relevance_scores=relevance_scores,
                clusters_used=clusters_used,
                processing_metadata=processing_metadata,
            )

        except Exception as e:
            debug_print(f"Error in context retrieval: {str(e)}")
            return ContextResponse(
                request_id=request.id,
                sources=[],
                relevance_scores={},
                clusters_used=[],
                processing_metadata={"error": str(e)},
            )

    async def _calculate_relevance_score(
        self, query: str, source: ContextSource
    ) -> float:
        """
        Calculate relevance score between query and source.

        Args:
            query: User query
            source: Context source to evaluate

        Returns:
            Relevance score between 0 and 1
        """
        try:
            # Simple TF-IDF based relevance (can be enhanced with embeddings)
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            # Combine query and source content
            documents = [query, source.content]

            # Calculate TF-IDF vectors
            vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(documents)

            # Calculate cosine similarity using getrow for sparse matrices
            query_vector = tfidf_matrix.getrow(0)
            source_vector = tfidf_matrix.getrow(1)
            similarity = cosine_similarity(query_vector, source_vector)
            score = float(similarity[0][0])

            # Boost score based on metadata matches
            metadata_boost = 0.0
            query_lower = query.lower()

            # Check keywords match
            keywords = source.metadata.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    metadata_boost += 0.1

            # Check title/name match
            if source.name.lower() in query_lower or any(
                word in source.name.lower() for word in query_lower.split()
            ):
                metadata_boost += 0.2

            # Apply boost and cap at 1.0
            final_score = min(1.0, score + metadata_boost)

            return final_score

        except Exception as e:
            debug_print(f"Error calculating relevance score: {str(e)}")
            return 0.0

    async def ensure_initialized(self) -> None:
        """Ensure the Context7 engine is properly initialized."""
        if not self._initialized and not self._initialization_task:
            self._initialization_task = asyncio.create_task(
                self._initialize_context_sources()
            )

        if self._initialization_task and not self._initialized:
            try:
                await self._initialization_task
                self._initialized = True
            except Exception as e:
                debug_print(f"Context7 initialization failed: {e}")
                self._initialization_task = None

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get diagnostic information about the Context7 engine.

        Returns:
            Dictionary containing diagnostic information
        """
        return {
            "context_sources_loaded": len(self.context_sources),
            "context_clusters_created": len(self.context_clusters),
            "requests_processed": self.requests_processed,
            "vectorizer_features": (
                self.source_vectors.shape[1] if self.source_vectors is not None else 0
            ),
            "knowledge_directories": self.knowledge_dirs,
            "engine_status": "operational" if self.context_sources else "no_sources",
        }
