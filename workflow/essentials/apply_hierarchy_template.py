import json
from typing import Any, Dict, List, Optional

import ayon_api
from taskflow.engines.action_engine import engine

from ayon_workflow.datatypes import FolderItem
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class ApplyHierarchyTemplate(WorkflowTaskNode):
    """Create folders and tasks under an AYON folder from a template,
    skipping the ones that are already there."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="folder",
            description="The folder to create them in.",
        ),
        InputAttribute(
            name="template",
            description=(
                "The hierarchy as JSON, as the Power Pack hierarchy "
                'templates: {"entities": [{"entity_type": "folder" or '
                '"task", "entity_subtype": its type, "name", "label", '
                '"status", "attrib", "assignees", "entities": [...]}]}.'
            ),
            widget={"name": "code"},
        ),
    ]
    outputs = [
        OutputAttribute(
            name="folder_context",
            description="The folder.",
        )
    ]

    def execute(
        self,
        folder: FolderItem,
        template: str,
        _engine: Optional[engine.ActionEngine] = None,
    ) -> FolderItem:
        template = json.loads(template)
        created: List[List[str]] = []
        try:
            self._create(
                folder.project_name,
                folder.folder_id,
                template.get("entities") or [],
                created,
            )
        finally:
            # kept to remove them if this or a later node fails
            self.inject_custom_backend_data(_engine, created=created)
        return folder

    def _create(
        self,
        project_name: str,
        folder_id: str,
        entities: List[Dict[str, Any]],
        created: List[List[str]],
    ):
        existing = {
            (folder["name"].lower(), "folder"): folder["id"]
            for folder in ayon_api.get_folders(
                project_name, parent_ids=[folder_id], active=None
            )
        }
        existing.update({
            (task["name"].lower(), "task"): task["id"]
            for task in ayon_api.get_tasks(
                project_name, folder_ids=[folder_id], active=None
            )
        })
        for entity in entities:
            entity_type = entity.get("entity_type")
            if entity_type not in ("folder", "task"):
                raise ValueError(
                    f"{entity_type!r} is not folder or task in {entity}."
                )
            key = (entity["name"].lower(), entity_type)
            entity_id = existing.get(key)
            if entity_id is None:
                fields = {
                    "label": entity.get("label"),
                    "status": entity.get("status"),
                    "attrib": entity.get("attrib"),
                }
                if entity_type == "folder":
                    entity_id = ayon_api.create_folder(
                        project_name,
                        entity["name"],
                        folder_type=entity.get("entity_subtype"),
                        parent_id=folder_id,
                        **fields,
                    )
                else:
                    entity_id = ayon_api.create_task(
                        project_name,
                        entity["name"],
                        entity.get("entity_subtype"),
                        folder_id,
                        assignees=entity.get("assignees"),
                        **fields,
                    )
                created.append([entity_type, entity_id])

            if entity_type == "folder":
                self._create(
                    project_name,
                    entity_id,
                    entity.get("entities") or [],
                    created,
                )

    def revert_execute(
        self,
        folder: FolderItem,
        template: str,
        _custom_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        # children first: a folder with tasks cannot be deleted
        for entity_type, entity_id in reversed(
            (_custom_data or {}).get("created") or []
        ):
            if entity_type == "folder":
                ayon_api.delete_folder(folder.project_name, entity_id)
            else:
                ayon_api.delete_task(folder.project_name, entity_id)
