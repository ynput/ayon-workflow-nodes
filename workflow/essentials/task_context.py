from typing import Optional

import ayon_api

from ayon_workflow.datatypes import TaskItem
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from .context import Context


class TaskContext(WorkflowTaskNode):
    """Gather a valid AYON task context."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="project_name",
            description="The project name",
        ),
        InputAttribute(
            name="task_id",
            description="An optional task id.",
        ),
        InputAttribute(
            name="task_path",
            description="An optional task path.",
        ),
        InputAttribute(
            name="ensure_exists",
            description="Assert context existence.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="task_context",
            description="The task context as a TaskItem.",
        )
    ]

    def execute(
        self,
        project_name: str,
        task_id: Optional[str] = None,
        task_path: Optional[str] = None,
        ensure_exists: Optional[bool] = True,
    ) -> TaskItem:
        if not task_id and (not task_path):
            raise ValueError("Either task_id or task_path must be provided.")

        if task_id:
            task_dict = ayon_api.get_task_by_id(project_name, task_id) or {}
            task_name = task_dict.get("name", "unknown")
            folder_path = None
            folder_id = task_dict.get("folderId", "unknown")
        else:
            folder_path, task_name = task_path.rsplit("/", 1)
            folder_id = None

        return Context().execute(
            project_name,
            folder_id=folder_id,
            folder_path=folder_path,
            task_name=task_name,
            ensure_exists=ensure_exists,
        )
