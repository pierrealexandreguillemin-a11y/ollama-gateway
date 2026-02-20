"""
RAG (Retrieval-Augmented Generation) Engine
Local vector embeddings with Ollama + semantic search
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
import httpx
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Local RAG engine using Ollama embeddings
    No external dependencies - 100% local
    """

    def __init__(self, ollama_url: str = "http://localhost:11434", storage_path: str = "./rag_storage"):
        self.ollama_url = ollama_url
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Embedding model (Ollama nomic-embed-text)
        self.embedding_model = "nomic-embed-text"

        # Vector store (simple JSON for v2.0, can upgrade to ChromaDB later)
        self.vectors_file = self.storage_path / "vectors.json"
        self.documents_file = self.storage_path / "documents.json"

        # Load existing data
        self.vectors = self._load_vectors()
        self.documents = self._load_documents()

        logger.info(f"RAG Engine initialized with {len(self.documents)} documents")

    def _load_vectors(self) -> Dict[str, List[float]]:
        """Load vector embeddings from storage"""
        if self.vectors_file.exists():
            with open(self.vectors_file, 'r') as f:
                return json.load(f)
        return {}

    def _load_documents(self) -> Dict[str, Dict[str, Any]]:
        """Load document metadata from storage"""
        if self.documents_file.exists():
            with open(self.documents_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_vectors(self):
        """Persist vectors to disk"""
        with open(self.vectors_file, 'w') as f:
            json.dump(self.vectors, f)

    def _save_documents(self):
        """Persist documents to disk"""
        with open(self.documents_file, 'w') as f:
            json.dump(self.documents, f, indent=2)

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding vector from Ollama
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("embedding")
                else:
                    logger.error(f"Embedding API error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None

    async def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None
    ) -> bool:
        """
        Add a document to the RAG index

        Args:
            doc_id: Unique document identifier
            content: Text content to embed
            metadata: Additional metadata (title, source, etc.)
            project_id: Associated project ID
        """
        try:
            # Get embedding
            embedding = await self.get_embedding(content)

            if not embedding:
                return False

            # Store vector
            self.vectors[doc_id] = embedding

            # Store document
            self.documents[doc_id] = {
                "content": content,
                "metadata": metadata or {},
                "project_id": project_id,
                "embedding_model": self.embedding_model
            }

            # Persist
            self._save_vectors()
            self._save_documents()

            logger.info(f"Added document {doc_id} to RAG index")
            return True

        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def search(
        self,
        query: str,
        top_k: int = 5,
        project_id: Optional[str] = None,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in the RAG index

        Args:
            query: Search query
            top_k: Number of results to return
            project_id: Filter by project (optional)
            min_similarity: Minimum similarity threshold

        Returns:
            List of relevant documents with similarity scores
        """
        try:
            # Get query embedding
            query_embedding = await self.get_embedding(query)

            if not query_embedding:
                return []

            # Calculate similarities
            results = []

            for doc_id, doc_embedding in self.vectors.items():
                # Filter by project if specified
                if project_id:
                    doc_project = self.documents[doc_id].get("project_id")
                    if doc_project != project_id:
                        continue

                # Calculate similarity
                similarity = self.cosine_similarity(query_embedding, doc_embedding)

                if similarity >= min_similarity:
                    results.append({
                        "doc_id": doc_id,
                        "similarity": float(similarity),
                        "content": self.documents[doc_id]["content"],
                        "metadata": self.documents[doc_id]["metadata"],
                        "project_id": self.documents[doc_id].get("project_id")
                    })

            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def get_context_for_query(
        self,
        query: str,
        project_id: Optional[str] = None,
        max_tokens: int = 2000
    ) -> str:
        """
        Get relevant context for a query (for RAG-enhanced chat)

        Args:
            query: User query
            project_id: Current project
            max_tokens: Approximate max tokens for context

        Returns:
            Formatted context string
        """
        results = await self.search(query, top_k=5, project_id=project_id)

        if not results:
            return ""

        context_parts = []
        total_length = 0

        for i, result in enumerate(results, 1):
            content = result["content"]
            # Rough token estimation (4 chars ≈ 1 token)
            content_tokens = len(content) // 4

            if total_length + content_tokens > max_tokens:
                break

            context_parts.append(f"[Source {i}] {content}")
            total_length += content_tokens

        if context_parts:
            return "**Relevant Context:**\n\n" + "\n\n".join(context_parts)

        return ""

    def delete_document(self, doc_id: str) -> bool:
        """Remove a document from the index"""
        try:
            if doc_id in self.vectors:
                del self.vectors[doc_id]
                del self.documents[doc_id]
                self._save_vectors()
                self._save_documents()
                logger.info(f"Deleted document {doc_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    def clear_project(self, project_id: str) -> int:
        """Delete all documents for a project"""
        deleted = 0
        docs_to_delete = [
            doc_id for doc_id, doc in self.documents.items()
            if doc.get("project_id") == project_id
        ]

        for doc_id in docs_to_delete:
            if self.delete_document(doc_id):
                deleted += 1

        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG engine statistics"""
        projects = set(
            doc.get("project_id") for doc in self.documents.values()
            if doc.get("project_id")
        )

        return {
            "total_documents": len(self.documents),
            "total_projects": len(projects),
            "embedding_model": self.embedding_model,
            "storage_path": str(self.storage_path),
            "storage_size_mb": self._get_storage_size()
        }

    def _get_storage_size(self) -> float:
        """Get storage size in MB"""
        total = 0
        for file in self.storage_path.glob("*"):
            if file.is_file():
                total += file.stat().st_size
        return round(total / (1024 * 1024), 2)
