from typing import Union

import ayon_api

from ayon_workflow.datatypes import TaskItem
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class AssignUsers(WorkflowTaskNode):
    """Assign users to an AYON task, or take them off it."""

    EDIT_MODES = ["add", "remove", "replace"]

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="task",
            description="The task to assign.",
        ),
        InputAttribute(
            name="users",
            description="User names.",
            # editors can offer the users of the project
            widget={"name": "users"},
        ),
        InputAttribute(
            name="edit_mode",
            description=(
                "Add them to the assignees, remove them, or make them the "
                "only assignees."
            ),
            default="add",
            widget={"name": "choice", "options": EDIT_MODES},
        ),
    ]
    outputs = [
        OutputAttribute(
            name="task_context",
            description="The task with its new assignees.",
        )
    ]

    def execute(
        self,
        task: TaskItem,
        users: Union[str, list[str]],
        edit_mode: str = "add",
    ) -> TaskItem:
        if edit_mode not in self.EDIT_MODES:
            raise ValueError(
                f"Invalid edit mode: {edit_mode}, "
                f"must be one of {self.EDIT_MODES}"
            )
        if isinstance(users, str):
            users = [users]
        users = [name for name in users if name]

        known = {
            user["name"]
            for user in ayon_api.get_users(usernames=users, fields={"name"})
        }
        unknown = [name for name in users if name not in known]
        if unknown:
            raise ValueError(f"No such user: {', '.join(unknown)}.")

        data = ayon_api.get_task_by_id(
            task.project_name, task.task_id, fields={"assignees"}
        ) or {}
        current = list(data.get("assignees") or [])
        if edit_mode == "add":
            assignees = current + [
                name for name in users if name not in current
            ]
        elif edit_mode == "remove":
            assignees = [name for name in current if name not in users]
        else:
            assignees = users

        # kept to restore them if a later node fails
        self._previous = current
        ayon_api.update_task(
            task.project_name, task.task_id, assignees=assignees
        )
        return task

    def revert_execute(
        self,
        task: TaskItem,
        users: Union[str, list[str]],
        edit_mode: str = "add",
        **kwargs,
    ):
        if hasattr(self, "_previous"):
            ayon_api.update_task(
                task.project_name, task.task_id, assignees=self._previous
            )
