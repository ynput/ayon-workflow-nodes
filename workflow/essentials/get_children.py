import re
from typing import Dict, List, Tuple

import ayon_api

from ayon_workflow.datatypes import (
    Entity,
    FolderItem,
    ProductItem,
    TaskItem,
    VersionItem,
)
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from . import _utils


class GetChildren(WorkflowTaskNode):
    """Get the folders or tasks of an AYON folder, or the versions
    published from a task."""

    CHILD_TYPES = ["folder", "task", "version"]

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_entity",
            description="The folder, or the task for versions.",
        ),
        InputAttribute(
            name="child_type",
            description="The children to get.",
            widget={"name": "choice", "options": CHILD_TYPES},
        ),
        InputAttribute(
            name="recursive",
            description=(
                "Also the folders and tasks of its sub-folders, at any depth."
            ),
        ),
        InputAttribute(
            name="latest_only",
            description="Only the latest version of each product.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="children",
            description="The children.",
        ),
        OutputAttribute(
            name="statuses",
            description="Their statuses, in the same order.",
        ),
    ]

    def execute(
        self,
        input_entity: Entity,
        child_type: str = "task",
        recursive: bool = False,
        latest_only: bool = False,
    ) -> Tuple[List[Entity], List[str]]:
        project_name = input_entity.project_name
        folders: Dict[str, FolderItem] = {}

        def folder_item(folder_id: str) -> FolderItem:
            if folder_id not in folders:
                folders[folder_id] = _utils.get_folder_item(
                    project_name, folder_id=folder_id
                )
            return folders[folder_id]

        entity_type = getattr(input_entity, "entity_type", None)
        if child_type == "version" and entity_type == "task":
            versions = list(ayon_api.get_versions(
                project_name,
                task_ids=[input_entity.task_id],
                hero=False,
                latest=True if latest_only else None,
            ))
            products = {
                product["id"]: product
                for product in ayon_api.get_products(
                    project_name,
                    product_ids={v["productId"] for v in versions},
                )
            }
            children = [
                VersionItem(
                    version_id=version["id"],
                    product=ProductItem(
                        product_id=version["productId"],
                        folder=folder_item(
                            products[version["productId"]]["folderId"]
                        ),
                    ),
                    version=version["version"],
                )
                for version in versions
            ]
            return children, [version["status"] for version in versions]

        if child_type not in ("folder", "task") or entity_type != "folder":
            raise ValueError(
                f"Cannot get the {child_type}s of a {entity_type}: folders "
                "and tasks are taken from a folder, versions from a task."
            )

        if recursive:
            path = ayon_api.get_folder_by_id(
                project_name, input_entity.folder_id, fields={"path"}
            )["path"]
            sub_folders = list(ayon_api.get_folders(
                project_name, folder_path_regex=f"^{re.escape(path)}/"
            ))
        else:
            sub_folders = list(ayon_api.get_folders(
                project_name, parent_ids=[input_entity.folder_id]
            ))

        if child_type == "folder":
            children = [folder_item(folder["id"]) for folder in sub_folders]
            return children, [folder["status"] for folder in sub_folders]

        folder_ids = [input_entity.folder_id]
        if recursive:
            folder_ids += [folder["id"] for folder in sub_folders]
        tasks = list(ayon_api.get_tasks(project_name, folder_ids=folder_ids))
        children = []
        for task in tasks:
            folder = folder_item(task["folderId"])
            children.append(TaskItem(
                project_name=project_name,
                folder_type=folder.folder_type,
                folder_name=folder.folder_name,
                folder_id=folder.folder_id,
                _parent=folder.parent,
                task_id=task["id"],
                task_name=task["name"],
                task_type=task["taskType"],
            ))
        return children, [task["status"] for task in tasks]
