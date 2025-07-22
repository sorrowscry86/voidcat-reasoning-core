#!/usr/bin/env python3
"""
VoidCat Reasoning Core - Multi-Format Document Processor

This module provides processors for different document formats:
- Markdown (.md)
- Text (.txt)
- PDF (.pdf)
- JSON (.json)
- JSON-LD (.jsonld)

Each processor extracts content and metadata from the document and
provides intelligent chunking based on document type and structure.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Try to import PDF processing library
try:
    import PyPDF2

    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class BaseProcessor:
    """Base class for document processors."""

    def extract(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract content and metadata from a document.

        Args:
            file_path: Path to the document

        Returns:
            Tuple of (content, metadata)
        """
        raise NotImplementedError("Subclasses must implement extract()")

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a document.

        Args:
            file_path: Path to the document

        Returns:
            Dictionary of metadata
        """
        file_path_obj = Path(file_path)
        return {
            "filename": file_path_obj.name,
            "extension": file_path_obj.suffix.lower(),
            "size_bytes": file_path_obj.stat().st_size if file_path_obj.exists() else 0,
            "last_modified": (
                file_path_obj.stat().st_mtime if file_path_obj.exists() else 0
            ),
        }


class MarkdownProcessor(BaseProcessor):
    """Processor for Markdown (.md) files."""

    def extract(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract content and metadata from a Markdown file."""
        metadata = self.get_metadata(file_path)
        metadata["type"] = "documentation"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title from first heading if available
            lines = content.split("\n")
            title = None
            for line in lines:
                if line.startswith("# "):
                    title = line.replace("# ", "").strip()
                    break

            if title:
                metadata["title"] = title

            # Count words for metadata
            word_count = len(content.split())
            metadata["word_count"] = word_count

            # Extract keywords from headings
            keywords = []
            for line in lines:
                if line.startswith("## ") or line.startswith("### "):
                    heading = line.replace("## ", "").replace("### ", "").strip()
                    keywords.extend(
                        [word.lower() for word in heading.split() if len(word) > 3]
                    )

            if keywords:
                metadata["keywords"] = list(set(keywords))[
                    :10
                ]  # Top 10 unique keywords

            return content, metadata

        except Exception as e:
            print(f"Error processing Markdown file {file_path}: {str(e)}")
            return "", metadata


class TextProcessor(BaseProcessor):
    """Processor for plain text (.txt) files."""

    def extract(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract content and metadata from a text file."""
        metadata = self.get_metadata(file_path)
        metadata["type"] = "text"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Count words for metadata
            word_count = len(content.split())
            metadata["word_count"] = word_count

            # Use filename as title
            metadata["title"] = Path(file_path).stem

            return content, metadata

        except Exception as e:
            print(f"Error processing text file {file_path}: {str(e)}")
            return "", metadata


class PDFProcessor(BaseProcessor):
    """Processor for PDF (.pdf) files."""

    def extract(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract content and metadata from a PDF file."""
        metadata = self.get_metadata(file_path)
        metadata["type"] = "pdf"

        if not PDF_SUPPORT:
            print(
                f"PDF processing not available. Install PyPDF2 to enable PDF support."
            )
            return "", metadata

        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)

                # Extract metadata
                pdf_info = pdf_reader.metadata
                if pdf_info:
                    if pdf_info.title:
                        metadata["title"] = pdf_info.title
                    if pdf_info.author:
                        metadata["author"] = pdf_info.author
                    if pdf_info.subject:
                        metadata["subject"] = pdf_info.subject
                    if pdf_info.creator:
                        metadata["creator"] = pdf_info.creator

                # Extract content
                content = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n\n"

                # Count words for metadata
                word_count = len(content.split())
                metadata["word_count"] = word_count
                metadata["page_count"] = len(pdf_reader.pages)

                # Use filename as title if not available in metadata
                if "title" not in metadata:
                    metadata["title"] = Path(file_path).stem

                return content, metadata

        except Exception as e:
            print(f"Error processing PDF file {file_path}: {str(e)}")
            return "", metadata


class JSONProcessor(BaseProcessor):
    """Processor for JSON (.json) files."""

    def extract(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract content and metadata from a JSON file."""
        metadata = self.get_metadata(file_path)
        metadata["type"] = "json"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # Convert JSON to string for processing
            content = json.dumps(json_data, indent=2)

            # Extract metadata from JSON if available
            if isinstance(json_data, dict):
                if "title" in json_data:
                    metadata["title"] = json_data["title"]
                if "description" in json_data:
                    metadata["description"] = json_data["description"]
                if "keywords" in json_data and isinstance(json_data["keywords"], list):
                    metadata["keywords"] = json_data["keywords"]

            # Count words for metadata
            word_count = len(content.split())
            metadata["word_count"] = word_count

            # Use filename as title if not available in metadata
            if "title" not in metadata:
                metadata["title"] = Path(file_path).stem

            return content, metadata

        except Exception as e:
            print(f"Error processing JSON file {file_path}: {str(e)}")
            return "", metadata


class JSONLDProcessor(BaseProcessor):
    """Processor for JSON-LD (.jsonld) files."""

    def extract(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract content and metadata from a JSON-LD file."""
        metadata = self.get_metadata(file_path)
        metadata["type"] = "jsonld"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                jsonld_data = json.load(f)

            # Convert JSON-LD to string for processing
            content = json.dumps(jsonld_data, indent=2)

            # Extract metadata from JSON-LD
            if isinstance(jsonld_data, dict):
                # Extract @context
                if "@context" in jsonld_data:
                    metadata["context"] = jsonld_data["@context"]

                # Extract @type
                if "@type" in jsonld_data:
                    metadata["document_type"] = jsonld_data["@type"]

                # Extract id
                if "id" in jsonld_data:
                    metadata["id"] = jsonld_data["id"]

                # Extract version
                if "version" in jsonld_data:
                    metadata["version"] = jsonld_data["version"]

                # Extract title
                if "title" in jsonld_data:
                    metadata["title"] = jsonld_data["title"]

                # Extract keywords
                if "keywords" in jsonld_data and isinstance(
                    jsonld_data["keywords"], list
                ):
                    metadata["keywords"] = jsonld_data["keywords"]

                # Extract content chunks if available
                if "content_chunks" in jsonld_data and isinstance(
                    jsonld_data["content_chunks"], list
                ):
                    chunks = []
                    for chunk in jsonld_data["content_chunks"]:
                        if "content" in chunk:
                            chunks.append(chunk["content"])

                    if chunks:
                        content = "\n\n".join(chunks)

            # Count words for metadata
            word_count = len(content.split())
            metadata["word_count"] = word_count

            # Use filename as title if not available in metadata
            if "title" not in metadata:
                metadata["title"] = Path(file_path).stem

            return content, metadata

        except Exception as e:
            print(f"Error processing JSON-LD file {file_path}: {str(e)}")
            return "", metadata


class MultiFormatProcessor:
    """Processor for multiple document formats."""

    def __init__(self):
        """Initialize the multi-format processor with format-specific processors."""
        self.processors = {
            ".md": MarkdownProcessor(),
            ".txt": TextProcessor(),
            ".pdf": PDFProcessor(),
            ".json": JSONProcessor(),
            ".jsonld": JSONLDProcessor(),
        }

    def process(self, file_path: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        Process a file with format-specific optimization.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (chunks, metadata)
        """
        extension = Path(file_path).suffix.lower()
        processor = self.processors.get(extension, self.processors[".txt"])

        content, metadata = processor.extract(file_path)
        chunks = self._intelligent_chunk(content, metadata)

        return chunks, metadata

    def _intelligent_chunk(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """
        Context-aware chunking based on content structure.

        Args:
            content: Document content
            metadata: Document metadata

        Returns:
            List of content chunks
        """
        if not content:
            return []

        doc_type = metadata.get("type", "")

        if doc_type == "documentation":
            return self._section_based_chunks(content)
        elif doc_type == "pdf":
            return self._page_based_chunks(content)
        elif doc_type in ["json", "jsonld"]:
            return self._structured_chunks(content)
        else:
            return self._sliding_window_chunks(content)

    def _section_based_chunks(
        self, content: str, max_chunk_size: int = 1000
    ) -> List[str]:
        """
        Chunk content based on sections (headings).

        Args:
            content: Document content
            max_chunk_size: Maximum chunk size in characters

        Returns:
            List of content chunks
        """
        lines = content.split("\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for line in lines:
            # Start a new chunk on headings
            if line.startswith("# ") or line.startswith("## "):
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0

            current_chunk.append(line)
            current_size += len(line)

            # Split if chunk gets too large
            if current_size >= max_chunk_size:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_size = 0

        # Add the last chunk if not empty
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _page_based_chunks(self, content: str) -> List[str]:
        """
        Chunk content based on pages (double newlines).

        Args:
            content: Document content

        Returns:
            List of content chunks
        """
        return content.split("\n\n")

    def _structured_chunks(self, content: str) -> List[str]:
        """
        Chunk structured content (JSON, JSON-LD).

        Args:
            content: Document content

        Returns:
            List of content chunks
        """
        try:
            data = json.loads(content)
            chunks = []

            if isinstance(data, dict):
                # Process each top-level key as a chunk
                for key, value in data.items():
                    if key.startswith("@"):
                        continue  # Skip JSON-LD metadata

                    chunk = f"{key}: {json.dumps(value, indent=2)}"
                    chunks.append(chunk)
            elif isinstance(data, list):
                # Process each list item as a chunk
                for item in data:
                    chunk = json.dumps(item, indent=2)
                    chunks.append(chunk)

            # If no chunks were created, use the whole content
            if not chunks:
                chunks = [content]

            return chunks

        except json.JSONDecodeError:
            # If JSON parsing fails, fall back to sliding window
            return self._sliding_window_chunks(content)

    def _sliding_window_chunks(
        self, content: str, chunk_size: int = 500, overlap: int = 50
    ) -> List[str]:
        """
        Chunk content using a sliding window approach.

        Args:
            content: Document content
            chunk_size: Size of each chunk in words
            overlap: Overlap between chunks in words

        Returns:
            List of content chunks
        """
        words = content.split()
        chunks = []

        if len(words) <= chunk_size:
            return [content]

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)

        return chunks

    def discover_files(self, directory: str) -> List[str]:
        """
        Discover all supported files in a directory.

        Args:
            directory: Directory to search

        Returns:
            List of file paths
        """
        supported_extensions = list(self.processors.keys())
        files = []

        for ext in supported_extensions:
            pattern = f"*{ext}"
            for file_path in Path(directory).glob(pattern):
                files.append(str(file_path))

        return files


# Example usage
if __name__ == "__main__":
    processor = MultiFormatProcessor()

    # Test with a sample markdown file
    knowledge_dir = "knowledge_source"
    files = processor.discover_files(knowledge_dir)

    print(f"Found {len(files)} files in {knowledge_dir}:")
    for file in files:
        print(f"  - {file}")
        chunks, metadata = processor.process(file)
        print(f"    Metadata: {metadata}")
        print(f"    Chunks: {len(chunks)}")
