from typing import Optional

import ayon_api

from ayon_workflow.datatypes import ContextItem, ProjectItem
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from ._utils import get_folder_item, get_task_item


class Context(WorkflowTaskNode):
    """Gather a valid AYON context item."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="project_name",
            description="The project name",
        ),
        InputAttribute(
            name="folder_id",
            description="An optional folder ID.",
        ),
        InputAttribute(
            name="folder_path",
            description="An optional folder path.",
        ),
        InputAttribute(
            name="task_name",
            description="An optional task name.",
        ),
        InputAttribute(
            name="task_type",
            description="An optional task type.",
        ),
        InputAttribute(
            name="ensure_exists",
            description="Assert context existence.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="context",
            description="The resolved context.",
        )
    ]

    def execute(
        self,
        project_name: str,
        folder_id: Optional[str] = None,
        folder_path: Optional[str] = None,
        task_name: Optional[str] = None,
        task_type: Optional[str] = None,
        ensure_exists: Optional[bool] = True,
    ) -> ContextItem:
        if not project_name:
            raise ValueError("No project name provided.")

        if ensure_exists and (not ayon_api.get_project(project_name)):
            raise ValueError(f"Project {project_name} does not exist.")

        if folder_id or folder_path:
            folder_item = get_folder_item(
                project_name,
                folder_path=folder_path,
                folder_id=folder_id,
                ensure_exists=ensure_exists,
            )
            if task_name:
                return get_task_item(
                    project_name,
                    folder_item,
                    task_name,
                    task_type=task_type,
                    ensure_exists=ensure_exists,
                )
            return folder_item

        return ProjectItem(project_name=project_name)
