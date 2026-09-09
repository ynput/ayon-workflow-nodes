from typing import Union

import ayon_api

from ayon_workflow.datatypes import (
    FolderItem,
    TaskItem,
)
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class SetEntityWatchers(WorkflowTaskNode):
    """Set entity watcher(s) to an AYON context item."""

    EDIT_MODES = ["add", "remove", "replace", "toggle"]

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_context",
            description="An AYON context item.",
        ),
        InputAttribute(
            name="watchers",
            description="A list of watchers to set.",
        ),
        InputAttribute(
            name="edit_mode",
            description="The mode used to edit watchers.",
            widget={
                "name": "choice",
                "options": EDIT_MODES,
            },
        ),
    ]
    outputs = [
        OutputAttribute(
            name="edited_context",
            description="The context with watchers set.",
        )
    ]

    def execute(
        self,
        input_context: Union[FolderItem, TaskItem],
        watchers: Union[str, list[str]],
        edit_mode: str = "add",
    ) -> Union[FolderItem, TaskItem]:
        if isinstance(watchers, str):
            watchers = [watchers]

        if edit_mode not in self.EDIT_MODES:
            raise ValueError(
                f"Invalid edit mode: {edit_mode}, "
                f"must be one of {self.EDIT_MODES}"
            )

        if isinstance(input_context, TaskItem):
            entity_type = "task"
            entity_id = input_context.task_id
        else:
            entity_type = "folder"
            entity_id = input_context.folder_id

        if edit_mode in ("add", "remove", "toggle"):
            existing_watchers = ayon_api.get_entity_watchers(
                input_context.project_name,
                entity_id,
                entity_type,
            )

            if edit_mode == "remove":
                watchers = [
                    watcher for watcher in existing_watchers
                    if watcher not in watchers
                ]
            elif edit_mode == "toggle":
                # remove if already present, add if not
                watchers = watchers.copy()  # don't edit inplace.
                for watcher in existing_watchers:
                    if watcher in watchers:
                        watchers.remove(watcher)
                    else:
                        watchers.append(watcher)
            else:
                watchers = list(set(existing_watchers + watchers))

        ayon_api.set_entity_watchers(
            input_context.project_name,
            entity_id,
            entity_type,
            watchers,
        )

        return input_context
