from typing import Union

from ayon_workflow.datatypes import (
    ContextItem,
    FolderItem,
    ProjectItem,
    TaskItem,
)
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class GetParentContext(WorkflowTaskNode):
    """Get parent context of an AYON context item."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="context",
            description="An AYON context item.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="parent_context",
            description="The parent context.",
        )
    ]

    def execute(
        self,
        context: ContextItem,
    ) -> ContextItem:
        if isinstance(context, ProjectItem):
            return context

        if isinstance(context, TaskItem):
            return FolderItem(
                project_name=context.project_name,
                folder_type=context.folder_type,
                folder_name=context.folder_name,
                folder_id=context.folder_id,
                _parent=context.parent,
            )

        if context.parent:
            return context.parent

        return ProjectItem(project_name=context.project_name)
