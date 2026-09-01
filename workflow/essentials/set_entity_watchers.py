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
            name="replace",
            description="Whether to replace existing watchers.",
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
        replace: bool = False,
    ) -> Union[FolderItem, TaskItem]:
        if isinstance(watchers, str):
            watchers = [watchers]


        if isinstance(input_context, TaskItem):
            entity_type = "task"
            entity_id = input_context.task_id
        else:
            entity_type = "folder"
            entity_id = input_context.folder_id

        if not replace:
            existing_watchers = ayon_api.get_entity_watchers(
                input_context.project_name,
                entity_id,
                entity_type,
            )
            watchers = existing_watchers + watchers

        ayon_api.set_entity_watchers(
            input_context.project_name,
            entity_id,
            entity_type,
            watchers,
        )

        return input_context
