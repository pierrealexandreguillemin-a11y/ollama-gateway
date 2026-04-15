"""
Workspace Manager
Multi-project organization with tags, categories, and search
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """
    Manages multiple projects (workspaces) with advanced organization
    """

    def __init__(self, storage_path: str = "./workspaces"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        self.workspaces_file = self.storage_path / "workspaces.json"
        self.workspaces = self._load_workspaces()

        logger.info(f"WorkspaceManager initialized with {len(self.workspaces)} workspaces")

    def _load_workspaces(self) -> Dict[str, Dict[str, Any]]:
        """Load workspaces from storage"""
        if self.workspaces_file.exists():
            try:
                with open(self.workspaces_file, "r", encoding="utf-8") as f:
                    data: Dict[str, Dict[str, Any]] = json.load(f)
                    return data
            except Exception as e:
                logger.error(f"Failed to load workspaces: {e}")
                return {}
        return {}

    def _save_workspaces(self) -> None:
        """Persist workspaces to disk"""
        try:
            with open(self.workspaces_file, "w", encoding="utf-8") as f:
                json.dump(self.workspaces, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save workspaces: {e}")

    def create_workspace(
        self,
        name: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new workspace

        Args:
            name: Workspace name
            description: Workspace description
            tags: List of tags for organization
            category: Workspace category
            metadata: Additional metadata

        Returns:
            Created workspace object
        """
        workspace_id = f"ws_{int(datetime.now().timestamp() * 1000)}"

        workspace = {
            "id": workspace_id,
            "name": name,
            "description": description,
            "tags": tags or [],
            "category": category or "general",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0,
            "attachment_count": 0,
            "rag_doc_count": 0,
            "metadata": metadata or {},
            "settings": {
                "preferred_model": "auto",
                "enable_rag": True,
                "enable_attachments": True,
                "context_mode": "auto",  # auto, full, minimal
            },
        }

        self.workspaces[workspace_id] = workspace
        self._save_workspaces()

        logger.info(f"Created workspace: {name} ({workspace_id})")
        return workspace

    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        return self.workspaces.get(workspace_id)

    def update_workspace(
        self, workspace_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update workspace properties

        Args:
            workspace_id: Workspace ID
            updates: Dictionary of properties to update

        Returns:
            Updated workspace or None if not found
        """
        workspace = self.workspaces.get(workspace_id)

        if not workspace:
            return None

        # Update allowed fields
        allowed_fields = {"name", "description", "tags", "category", "metadata", "settings"}

        for key, value in updates.items():
            if key in allowed_fields:
                if key == "settings" and isinstance(value, dict):
                    # Merge settings
                    workspace["settings"].update(value)
                else:
                    workspace[key] = value

        workspace["updated_at"] = datetime.now().isoformat()

        self._save_workspaces()
        logger.info(f"Updated workspace: {workspace_id}")

        return workspace

    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace"""
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
            self._save_workspaces()
            logger.info(f"Deleted workspace: {workspace_id}")
            return True
        return False

    def list_workspaces(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List workspaces with optional filtering

        Args:
            category: Filter by category
            tags: Filter by tags (any match)
            search_query: Search in name/description

        Returns:
            List of matching workspaces
        """
        results = []

        for workspace in self.workspaces.values():
            # Category filter
            if category and workspace.get("category") != category:
                continue

            # Tags filter (any tag matches)
            if tags:
                workspace_tags = set(workspace.get("tags", []))
                if not any(tag in workspace_tags for tag in tags):
                    continue

            # Search query
            if search_query:
                query_lower = search_query.lower()
                name_match = query_lower in workspace.get("name", "").lower()
                desc_match = query_lower in workspace.get("description", "").lower()

                if not (name_match or desc_match):
                    continue

            results.append(workspace)

        # Sort by updated_at (most recent first)
        results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        return results

    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        categories = set()
        for workspace in self.workspaces.values():
            if workspace.get("category"):
                categories.add(workspace["category"])
        return sorted(list(categories))

    def get_all_tags(self) -> List[str]:
        """Get list of all tags used across workspaces"""
        tags = set()
        for workspace in self.workspaces.values():
            for tag in workspace.get("tags", []):
                tags.add(tag)
        return sorted(list(tags))

    def increment_stats(self, workspace_id: str, stat_name: str, amount: int = 1) -> None:
        """
        Increment workspace statistics

        Args:
            workspace_id: Workspace ID
            stat_name: Stat to increment (message_count, attachment_count, etc.)
            amount: Amount to increment
        """
        workspace = self.workspaces.get(workspace_id)

        if workspace and stat_name in workspace:
            workspace[stat_name] += amount
            workspace["updated_at"] = datetime.now().isoformat()
            self._save_workspaces()

    def get_stats(self) -> Dict[str, Any]:
        """Get overall workspace statistics"""
        total_messages = sum(ws.get("message_count", 0) for ws in self.workspaces.values())
        total_attachments = sum(ws.get("attachment_count", 0) for ws in self.workspaces.values())
        total_rag_docs = sum(ws.get("rag_doc_count", 0) for ws in self.workspaces.values())

        categories: Dict[str, int] = {}
        for workspace in self.workspaces.values():
            cat = workspace.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_workspaces": len(self.workspaces),
            "total_messages": total_messages,
            "total_attachments": total_attachments,
            "total_rag_documents": total_rag_docs,
            "categories": categories,
            "total_tags": len(self.get_all_tags()),
        }

    def search_across_workspaces(
        self, query: str, include_content: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search across all workspace metadata

        Args:
            query: Search query
            include_content: Whether to search message content (requires messages data)

        Returns:
            List of matching workspaces with context
        """
        query_lower = query.lower()
        results: List[Dict[str, Any]] = []

        for workspace in self.workspaces.values():
            score = 0
            matches = []

            # Search in name (higher weight)
            if query_lower in workspace.get("name", "").lower():
                score += 10
                matches.append("name")

            # Search in description
            if query_lower in workspace.get("description", "").lower():
                score += 5
                matches.append("description")

            # Search in tags
            for tag in workspace.get("tags", []):
                if query_lower in tag.lower():
                    score += 3
                    matches.append(f"tag:{tag}")

            # Search in category
            if query_lower in workspace.get("category", "").lower():
                score += 2
                matches.append("category")

            if score > 0:
                results.append(
                    {"workspace": workspace, "relevance_score": score, "matches": matches}
                )

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return results

    def export_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Export workspace data (without messages - for metadata only)"""
        workspace = self.workspaces.get(workspace_id)

        if not workspace:
            return None

        return {"workspace": workspace, "exported_at": datetime.now().isoformat(), "version": "2.0"}

    def import_workspace(self, workspace_data: Dict[str, Any]) -> Optional[str]:
        """Import workspace from exported data"""
        try:
            workspace = workspace_data.get("workspace")

            if not workspace:
                return None

            # Generate new ID
            new_id = f"ws_{int(datetime.now().timestamp() * 1000)}"
            workspace["id"] = new_id
            workspace["created_at"] = datetime.now().isoformat()
            workspace["updated_at"] = datetime.now().isoformat()

            self.workspaces[new_id] = workspace
            self._save_workspaces()

            logger.info(f"Imported workspace: {workspace.get('name')} as {new_id}")
            return new_id

        except Exception as e:
            logger.error(f"Failed to import workspace: {e}")
            return None
