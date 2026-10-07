from typing import Optional

import ayon_api

from ayon_workflow.datatypes import (
    TaskItem,
    VersionItem,
)
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from . import _utils


class GetVersionTask(WorkflowTaskNode):
    """Get the task an AYON version was published from."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="version_item",
            description="An AYON version.",
        ),
        InputAttribute(
            name="ensure_exists",
            description="Assert version published against a task.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="task_context",
            description="The task the version was published from.",
        )
    ]

    def execute(
        self,
        version_item: VersionItem,
        ensure_exists: bool = True,
    ) -> Optional[TaskItem]:
        project_name = version_item.project_name
        version_data = ayon_api.get_version_by_id(
            project_name,
            version_item.id,
            fields={"taskId"},
        ) or {}
        task_id = version_data.get("taskId")
        if not task_id:
            if ensure_exists:
                raise ValueError(
                    f"Version {version_item.version} ({version_item.id}) "
                    "was not published from a task."
                )
            else:
                return None

        task_data = ayon_api.get_task_by_id(project_name, task_id)
        if not task_data:
            raise ValueError(f"Task {task_id} of the version does not exist.")

        folder_item = _utils.get_folder_item(
            project_name,
            folder_id=task_data["folderId"],
        )
        return _utils.get_task_item(
            project_name,
            folder_item,
            task_data["name"],
        )
