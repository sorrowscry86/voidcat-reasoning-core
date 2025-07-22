# VoidCat Reasoning Core - Enhanced Components

This document provides an overview of the enhanced components implemented for the VoidCat Reasoning Core system.

## Multi-Format Processor

The Multi-Format Processor (`multi_format_processor.py`) enables the VoidCat Reasoning Core to process documents in various formats:

- **Markdown (.md)**: Documentation and knowledge base articles
- **Text (.txt)**: Plain text documents
- **PDF (.pdf)**: PDF documents (requires PyPDF2)
- **JSON (.json)**: Structured data in JSON format
- **JSON-LD (.jsonld)**: Linked data in JSON-LD format

### Key Features

- **Format-specific Processing**: Each format has a dedicated processor that extracts content and metadata
- **Intelligent Chunking**: Documents are chunked based on their type and structure
- **Metadata Extraction**: Rich metadata is extracted from each document
- **File Discovery**: Automatic discovery of supported files in the knowledge base

### Usage Example

```python
from multi_format_processor import MultiFormatProcessor

# Initialize processor
processor = MultiFormatProcessor()

# Discover files
knowledge_dir = "knowledge_source"
files = processor.discover_files(knowledge_dir)

# Process files
for file in files:
    chunks, metadata = processor.process(file)
    print(f"Processed {file}: {len(chunks)} chunks")
```

## Hybrid Vectorizer

The Hybrid Vectorizer (`hybrid_vectorizer.py`) provides advanced document vectorization and retrieval capabilities:

- **TF-IDF Vectorization**: Keyword-based document representation
- **Semantic Embeddings**: Meaning-based document representation using OpenAI embeddings
- **Vector Compression**: Efficient storage of document vectors
- **Index Caching**: Fast startup through cached indexes

### Key Features

- **Hybrid Retrieval**: Combines TF-IDF and semantic similarity for better results
- **Metadata Indexing**: Rich metadata for improved retrieval
- **Efficient Storage**: Compressed vector storage for reduced memory usage
- **Fast Startup**: Cached indexes for quick initialization

### Usage Example

```python
from hybrid_vectorizer import HybridVectorizer

# Initialize vectorizer
vectorizer = HybridVectorizer(
    tfidf_features=5000,
    semantic_embeddings=True,
    compression_enabled=True
)

# Build index
index = vectorizer.build_index(documents, metadata)

# Query index
results = vectorizer.query("What is sequential thinking?", top_k=3)
for result in results:
    print(f"Similarity: {result['similarity']}")
    print(f"Content: {result['content'][:100]}...")
```

## Knowledge Base Expansion

The knowledge base has been expanded with new document formats:

- **JSON-LD Documents**: Structured knowledge with semantic annotations
- **Text Documents**: Plain text documents with rich content

### JSON-LD Format

The JSON-LD format provides structured knowledge with semantic annotations:

```json
{
  "@context": "https://voidcat.dev/knowledge/v2",
  "@type": "OptimizedKnowledgeDocument",
  "id": "document-id",
  "version": "1.0",
  "title": "Document Title",
  "description": "Document Description",
  "keywords": ["keyword1", "keyword2"],
  "content_chunks": [
    {
      "chunk_id": "chunk_001",
      "content": "Chunk content...",
      "keywords": ["keyword1", "keyword2"],
      "relevance_boost": 1.2,
      "chunk_type": "introduction"
    }
  ]
}
```

## Testing

The enhanced components have been tested with the following scripts:

- **test_multi_format.py**: Tests the Multi-Format Processor
- **test_hybrid_vectorizer.py**: Tests the Hybrid Vectorizer
- **test_knowledge_retrieval.py**: Tests retrieval from the expanded knowledge base

## Next Steps

The next phase of development will focus on:

1. Enhancing the Sequential Thinking engine with complexity-based routing
2. Improving the Context7 integration with multi-dimensional retrieval
3. Adding performance monitoring and optimization
4. Creating a unified architecture with adaptive routing

---

*Last Updated: July 5, 2025*