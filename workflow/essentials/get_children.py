import re
from typing import Callable, Dict, List, Optional, Tuple

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


def _get_versions(
    project_name: str,
    task: TaskItem,
    latest_only: bool,
    folder_item: Callable[[str], FolderItem],
) -> Tuple[List[Entity], List[str]]:
    versions = list(ayon_api.get_versions(
        project_name,
        task_ids=[task.task_id],
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


def _get_sub_folders(
    project_name: str,
    folder: FolderItem,
    recursive: bool,
) -> List[dict]:
    if recursive:
        path = ayon_api.get_folder_by_id(
            project_name,
            folder.folder_id,
            fields={"path"}
        )["path"]

        return list(
            ayon_api.get_folders(
                project_name,
                folder_path_regex=f"^{re.escape(path)}/"
            )
        )

    return list(
        ayon_api.get_folders(
            project_name,
            parent_ids=[folder.folder_id]
        )
    )


def _get_tasks(
    project_name: str,
    folder_ids: List[str],
    folder_item: Callable[[str], FolderItem],
) -> Tuple[List[Entity], List[str]]:
    tasks = list(ayon_api.get_tasks(project_name, folder_ids=folder_ids))
    children = []
    for task in tasks:
        folder = folder_item(task["folderId"])
        children.append(
            TaskItem(
                project_name=project_name,
                folder_type=folder.folder_type,
                folder_name=folder.folder_name,
                folder_id=folder.folder_id,
                _parent=folder.parent,
                task_id=task["id"],
                task_name=task["name"],
                task_type=task["taskType"],
            )
        )
    return children, [task["status"] for task in tasks]


class GetChildren(WorkflowTaskNode):
    """
    Get the children of an entity:
        - folders or tasks of an AYON folder,
        - versions published from a task.
    """

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
        InputAttribute(
            name="statuses",
            description=(
                "Only the children with one of these statuses (not case "
                "sensitive), all of them when empty."
            ),
        ),
    ]
    outputs = [
        OutputAttribute(
            name="children",
            description="The children with one of the statuses.",
        ),
        OutputAttribute(
            name="excluded_children",
            description="The other children.",
        ),
    ]

    def execute(
        self,
        input_entity: Entity,
        child_type: str = "task",
        recursive: bool = False,
        latest_only: bool = False,
        statuses: Optional[List[str]] = None,
    ) -> Tuple[List[Entity], List[Entity]]:
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
            folders[input_entity.folder_id] = FolderItem(
                project_name=project_name,
                folder_type=input_entity.folder_type,
                folder_name=input_entity.folder_name,
                folder_id=input_entity.folder_id,
                _parent=input_entity.parent,
            )
            children, child_statuses = _get_versions(
                project_name,
                input_entity,
                latest_only,
                folder_item
            )

        elif child_type in ("folder", "task") and entity_type == "folder":
            sub_folders = _get_sub_folders(
                project_name,
                input_entity,
                recursive
            )
            # parents first, so each one is built from the cache,
            # without fetching its ancestors again
            folders[input_entity.folder_id] = input_entity
            for folder in sorted(
                sub_folders,
                key=lambda f: f["path"].count("/")
            ):
                folders[folder["id"]] = FolderItem(
                    project_name=project_name,
                    folder_type=folder["folderType"],
                    folder_name=folder["name"],
                    folder_id=folder["id"],
                    _parent=folders[folder["parentId"]],
                )

            if child_type == "folder":
                children = [
                    folder_item(folder["id"]) for folder in sub_folders
                ]
                child_statuses = [folder["status"] for folder in sub_folders]
            else:
                folder_ids = [input_entity.folder_id]
                if recursive:
                    folder_ids += [folder["id"] for folder in sub_folders]
                children, child_statuses = _get_tasks(
                    project_name, folder_ids, folder_item
                )

        else:
            raise ValueError(
                f"Cannot get the {child_type}s of a {entity_type}: folders "
                "and tasks are taken from a folder, versions from a task."
            )

        if not statuses:
            return children, []

        wanted = {status.lower() for status in statuses}
        kept, excluded = [], []
        for child, status in zip(children, child_statuses):
            if status.lower() in wanted:
                kept.append(child)
            else:
                excluded.append(child)
        return kept, excluded
