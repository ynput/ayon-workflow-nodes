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
        )
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
    ) -> Union[FolderItem, TaskItem]:
        if isinstance(watchers, str):
            watchers = [watchers]

        entity_type = (
            "task" if isinstance(input_context, TaskItem)
            else "folder"
        )
        ayon_api.set_entity_watchers(
            input_context.project_name,
            input_context.folder_id,
            entity_type,
            watchers,
        )

        return input_context
