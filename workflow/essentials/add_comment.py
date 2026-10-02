import ayon_api

from ayon_workflow.datatypes import Entity
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

ENTITY_TYPES = ("folder", "task", "product", "version")


class AddComment(WorkflowTaskNode):
    """Comment on an AYON folder, task, product or version, in its activity
    feed."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_entity",
            description="The folder, task, product or version.",
        ),
        InputAttribute(
            name="text",
            description="The comment, Markdown like comments in AYON.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="edited_entity",
            description="The entity commented on.",
        )
    ]

    def execute(self, input_entity: Entity, text: str) -> Entity:
        if getattr(input_entity, "entity_type", None) not in ENTITY_TYPES:
            raise ValueError(
                f"Cannot comment on {input_entity}, expected a folder, task, "
                "product or version."
            )
        if not text or not text.strip():
            raise ValueError("No comment text.")
        self._activity_id = ayon_api.create_activity(
            input_entity.project_name,
            input_entity.id,
            input_entity.entity_type,
            "comment",
            body=text,
        )
        return input_entity

    def revert_execute(self, input_entity: Entity, text: str, **kwargs):
        if getattr(self, "_activity_id", None):
            ayon_api.delete_activity(
                input_entity.project_name, self._activity_id
            )
