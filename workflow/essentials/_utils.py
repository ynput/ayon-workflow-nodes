import tempfile

from dataclasses import asdict
from typing import Optional

import ayon_api

from ayon_workflow.datatypes import (
    FolderItem,
    TaskItem,
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


def check_parent_directory(
    parent_directory: Optional[str],
) -> str:
    if not parent_directory:
        parent_directory = tempfile.mkdtemp()

    return parent_directory
