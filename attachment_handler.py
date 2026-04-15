"""
Attachment Handler
File upload, parsing, and RAG integration
"""

import hashlib
import logging
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AttachmentHandler:
    """
    Handles file attachments for projects
    Supports: TXT, MD, PDF, code files, JSON, CSV
    """

    def __init__(self, storage_path: str = "./attachments"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Supported file types
        self.supported_extensions = {
            # Text formats
            ".txt",
            ".md",
            ".markdown",
            # Code
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".c",
            ".cpp",
            ".cs",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".html",
            ".css",
            ".scss",
            ".sql",
            # Data
            ".json",
            ".csv",
            ".xml",
            ".yaml",
            ".yml",
            ".toml",
            # Documentation
            ".pdf",
            ".rst",
            ".tex",
        }

        # Max file size (10MB)
        self.max_file_size = 10 * 1024 * 1024

        logger.info(f"AttachmentHandler initialized at {self.storage_path}")

    def _get_file_hash(self, content: bytes) -> str:
        """Generate unique hash for file content"""
        return hashlib.sha256(content).hexdigest()[:16]

    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF
        Simple implementation - can be enhanced with pypdf2 later
        """
        try:
            # For v2.0, we'll use simple extraction
            # In production, use PyPDF2 or pdfplumber
            return (
                f"[PDF Content from {file_path.name}]\n\n"
                "PDF parsing requires PyPDF2 library.\n"
                "Install: pip install pypdf2"
            )
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""

    def _parse_file_content(self, file_path: Path, mime_type: str) -> str:
        """
        Parse file content based on type
        """
        try:
            extension = file_path.suffix.lower()

            # PDF
            if extension == ".pdf":
                return self._extract_text_from_pdf(file_path)

            # Text-based files
            if extension in {
                ".txt",
                ".md",
                ".markdown",
                ".json",
                ".yaml",
                ".yml",
                ".csv",
                ".xml",
                ".toml",
                ".rst",
                ".tex",
            }:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()

            # Code files
            if extension in {
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".java",
                ".c",
                ".cpp",
                ".cs",
                ".go",
                ".rs",
                ".rb",
                ".php",
                ".html",
                ".css",
                ".scss",
                ".sql",
            }:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Add language identifier for better context
                    lang = extension[1:]  # Remove the dot
                    return f"```{lang}\n{content}\n```"

            # Fallback: try text
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            return f"[Error parsing file: {str(e)}]"

    async def save_attachment(
        self,
        filename: str,
        content: bytes,
        project_id: str,
        user_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Save an attachment and return metadata

        Args:
            filename: Original filename
            content: File content (bytes)
            project_id: Associated project ID
            user_metadata: Additional user-provided metadata

        Returns:
            Attachment metadata or None if failed
        """
        try:
            # Validate file size
            if len(content) > self.max_file_size:
                logger.warning(f"File {filename} exceeds max size")
                return None

            # Validate extension
            extension = Path(filename).suffix.lower()
            if extension not in self.supported_extensions:
                logger.warning(f"Unsupported file type: {extension}")
                return None

            # Generate unique ID
            file_hash = self._get_file_hash(content)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
            unique_filename = f"{timestamp}_{file_hash}_{safe_filename}"

            # Create project directory
            project_dir = self.storage_path / project_id
            project_dir.mkdir(exist_ok=True)

            # Save file
            file_path = project_dir / unique_filename
            with open(file_path, "wb") as f:
                f.write(content)

            # Get mime type
            mime_type, _ = mimetypes.guess_type(filename)

            # Parse content for RAG
            text_content = self._parse_file_content(file_path, mime_type or "")

            # Create metadata
            metadata = {
                "attachment_id": file_hash,
                "filename": filename,
                "stored_filename": unique_filename,
                "file_path": str(file_path),
                "size_bytes": len(content),
                "mime_type": mime_type,
                "extension": extension,
                "project_id": project_id,
                "uploaded_at": datetime.now().isoformat(),
                "text_content": text_content,
                "user_metadata": user_metadata or {},
            }

            logger.info(f"Saved attachment: {filename} ({len(content)} bytes)")
            return metadata

        except Exception as e:
            logger.error(f"Failed to save attachment: {e}")
            return None

    def get_attachment(self, project_id: str, attachment_id: str) -> Optional[Dict[str, Any]]:
        """Get attachment metadata"""
        try:
            project_dir = self.storage_path / project_id

            if not project_dir.exists():
                return None

            # Find file by ID (hash prefix)
            for file_path in project_dir.glob(f"*_{attachment_id}_*"):
                if file_path.is_file():
                    mime_type, _ = mimetypes.guess_type(str(file_path))

                    return {
                        "attachment_id": attachment_id,
                        "filename": file_path.name,
                        "file_path": str(file_path),
                        "size_bytes": file_path.stat().st_size,
                        "mime_type": mime_type,
                        "project_id": project_id,
                    }

            return None

        except Exception as e:
            logger.error(f"Failed to get attachment: {e}")
            return None

    def list_attachments(self, project_id: str) -> List[Dict[str, Any]]:
        """List all attachments for a project"""
        try:
            project_dir = self.storage_path / project_id

            if not project_dir.exists():
                return []

            attachments = []

            for file_path in project_dir.iterdir():
                if file_path.is_file():
                    # Extract hash from filename (format: timestamp_hash_filename)
                    parts = file_path.name.split("_", 2)
                    if len(parts) >= 3:
                        attachment_id = parts[1]
                    else:
                        attachment_id = file_path.stem

                    mime_type, _ = mimetypes.guess_type(str(file_path))

                    attachments.append(
                        {
                            "attachment_id": attachment_id,
                            "filename": file_path.name,
                            "size_bytes": file_path.stat().st_size,
                            "mime_type": mime_type,
                            "uploaded_at": datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).isoformat(),
                        }
                    )

            return attachments

        except Exception as e:
            logger.error(f"Failed to list attachments: {e}")
            return []

    def delete_attachment(self, project_id: str, attachment_id: str) -> bool:
        """Delete an attachment"""
        try:
            project_dir = self.storage_path / project_id

            if not project_dir.exists():
                return False

            # Find and delete file
            for file_path in project_dir.glob(f"*_{attachment_id}_*"):
                if file_path.is_file():
                    file_path.unlink()
                    logger.info(f"Deleted attachment: {attachment_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete attachment: {e}")
            return False

    def delete_project_attachments(self, project_id: str) -> int:
        """Delete all attachments for a project"""
        try:
            project_dir = self.storage_path / project_id

            if not project_dir.exists():
                return 0

            deleted = 0
            for file_path in project_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
                    deleted += 1

            # Remove empty directory
            if not any(project_dir.iterdir()):
                project_dir.rmdir()

            logger.info(f"Deleted {deleted} attachments from project {project_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to delete project attachments: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get attachment storage statistics"""
        try:
            total_files = 0
            total_size = 0
            projects = 0

            for project_dir in self.storage_path.iterdir():
                if project_dir.is_dir():
                    projects += 1
                    for file_path in project_dir.iterdir():
                        if file_path.is_file():
                            total_files += 1
                            total_size += file_path.stat().st_size

            return {
                "total_attachments": total_files,
                "total_projects": projects,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "supported_extensions": list(self.supported_extensions),
                "max_file_size_mb": self.max_file_size / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
