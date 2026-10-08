from typing import Any, Dict, Optional, Union

import ayon_api
from taskflow.engines.action_engine import engine

from ayon_workflow.datatypes import FolderItem, TaskItem
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from . import _utils


class CreateTask(WorkflowTaskNode):
    """Create a task in an AYON folder, or use the one with that name."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="folder",
            description="The folder to create the task in.",
        ),
        InputAttribute(
            name="task_name",
            description="The name of the task.",
        ),
        InputAttribute(
            name="task_type",
            description="One of the task types of the project.",
            # editors can offer the task types of the project
            widget={"name": "task_type"},
        ),
        InputAttribute(
            name="assignees",
            description="Users to assign when the task is created.",
            widget={"name": "users"},
        ),
    ]
    outputs = [
        OutputAttribute(
            name="task_context",
            description="The new task, or the one that was there.",
        )
    ]

    def execute(
        self,
        folder: FolderItem,
        task_name: str,
        task_type: str,
        assignees: Optional[Union[str, list[str]]] = None,
        _engine: Optional[engine.ActionEngine] = None,
    ) -> TaskItem:
        project_name = folder.project_name
        if not task_name:
            raise ValueError("No task name.")

        existing = ayon_api.get_task_by_name(
            project_name, folder.folder_id, task_name
        )
        if not existing:
            project = ayon_api.get_project(project_name) or {}
            names = [item["name"] for item in project.get("taskTypes") or []]
            matches = [
                name for name in names
                if name.lower() == (task_type or "").lower()
            ]
            if not matches:
                raise ValueError(
                    f"{task_type!r} is not a task type of project "
                    f"{project_name}. Expected one of: {', '.join(names)}."
                )
            if isinstance(assignees, str):
                assignees = [assignees]
            created_id = ayon_api.create_task(
                project_name,
                task_name,
                matches[0],
                folder.folder_id,
                assignees=[name for name in assignees or [] if name] or None,
            )
            self.inject_custom_backend_data(_engine, created_id=created_id)

        return _utils.get_task_item(project_name, folder, task_name)

    def revert_execute(
        self,
        folder: FolderItem,
        task_name: str,
        task_type: str,
        assignees: Optional[Union[str, list[str]]] = None,
        _custom_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        created_id = (_custom_data or {}).get("created_id")
        if created_id:
            ayon_api.delete_task(folder.project_name, created_id)
