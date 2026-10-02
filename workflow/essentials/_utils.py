import tempfile

from dataclasses import asdict
from typing import Optional, Tuple

import ayon_api

from ayon_workflow.datatypes import (
    Entity,
    FolderItem,
    ProductItem,
    TaskItem,
    VersionItem,
)


def get_task_item(
    project_name: str,
    folder_item: FolderItem,
    task_name: str,
    task_type: Optional[str] = None,
    ensure_exists: Optional[bool] = True,
) -> TaskItem:
    if ensure_exists:
        task_dict = ayon_api.get_task_by_name(
            project_name,
            folder_item.folder_id,
            task_name,
        )

        if not task_dict or (
            task_type and task_dict.get("taskType") != task_type
        ):
            raise ValueError(
                f"No task {task_name} ({task_type}) under {folder_item}."
            )

        attrs = asdict(folder_item)
        attrs["_parent"] = folder_item.parent
        attrs["task_id"] = task_dict["id"]
        attrs["task_name"] = task_name
        attrs["task_type"] = task_dict.get("taskType")
        return TaskItem(**attrs)

    raise NotImplementedError("Promised task is not implemented yet.")


def get_folder_item(
    project_name: str,
    folder_id: Optional[str] = None,
    folder_path: Optional[str] = None,
    ensure_exists: Optional[bool] = True,
) -> FolderItem:
    if ensure_exists:
        if not (folder_id or folder_path):
            raise ValueError("Missing folder_path or folder_id.")

        if folder_id:
            folder_dict = ayon_api.get_folder_by_id(
                project_name,
                folder_id,
            )

        else:
            folder_dict = ayon_api.get_folder_by_path(
                project_name, folder_path
            )

        if folder_dict:
            if folder_dict["parentId"]:
                parent_folder = get_folder_item(
                    project_name, folder_id=folder_dict["parentId"]
                )
            else:
                parent_folder = None

            return FolderItem(
                folder_type=folder_dict["folderType"],
                folder_name=folder_dict["name"],
                folder_id=folder_dict["id"],
                project_name=project_name,
                _parent=parent_folder,
            )

        raise ValueError(
            "Provided folder does not exists for "
            f"project_name={project_name} "
            f"folder_path={folder_path} "
            f"folder_id={folder_id}."
        )

    raise NotImplementedError("Promised folder is not implemented yet.")


def get_entity_item(
    project_name: str,
    entity_type: str,
    entity_id: str,
) -> Entity:
    """ The workflow item of an AYON folder, task, product or version.
    """
    if entity_type == "folder":
        return get_folder_item(project_name, folder_id=entity_id)

    if entity_type == "task":
        task = ayon_api.get_task_by_id(project_name, entity_id)
        if not task:
            raise ValueError(f"Task {entity_id} does not exist.")
        folder_item = get_folder_item(
            project_name, folder_id=task["folderId"]
        )
        return get_task_item(project_name, folder_item, task["name"])

    if entity_type in ("product", "version"):
        version = None
        product_id = entity_id
        if entity_type == "version":
            version = ayon_api.get_version_by_id(project_name, entity_id)
            if not version:
                raise ValueError(f"Version {entity_id} does not exist.")
            product_id = version["productId"]

        product = ayon_api.get_product_by_id(project_name, product_id)
        if not product:
            raise ValueError(f"Product {product_id} does not exist.")
        product_item = ProductItem(
            product_id=product_id,
            folder=get_folder_item(
                project_name, folder_id=product["folderId"]
            ),
        )
        if version is None:
            return product_item
        return VersionItem(
            version_id=entity_id,
            product=product_item,
            version=version["version"],
        )

    raise ValueError(
        f"{entity_type!r} is not a folder, task, product or version."
    )


_ENTITY_FUNCTIONS = {
    "folder": ("get_folder_by_id", "update_folder"),
    "task": ("get_task_by_id", "update_task"),
    "product": ("get_product_by_id", "update_product"),
    "version": ("get_version_by_id", "update_version"),
}


def _entity_functions(entity: Entity) -> Tuple[str, str]:
    entity_type = getattr(entity, "entity_type", None)
    if entity_type not in _ENTITY_FUNCTIONS:
        raise ValueError(
            f"Expected a folder, task, product or version, got {entity}."
        )
    return _ENTITY_FUNCTIONS[entity_type]


def get_entity_data(
    entity: Entity,
    fields: Optional[set] = None,
) -> dict:
    """ The server data of a folder, task, product or version item.
    """
    getter, _ = _entity_functions(entity)
    return getattr(ayon_api, getter)(
        entity.project_name, entity.id, fields=fields
    ) or {}


def update_entity(entity: Entity, **changes):
    """ Update a folder, task, product or version on the server.
    """
    _, update = _entity_functions(entity)
    getattr(ayon_api, update)(entity.project_name, entity.id, **changes)


def check_parent_directory(
    parent_directory: Optional[str],
) -> str:
    if not parent_directory:
        parent_directory = tempfile.mkdtemp()

    return parent_directory
