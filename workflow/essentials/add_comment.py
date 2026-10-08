from typing import Any, Dict, Optional

import ayon_api
from taskflow.engines.action_engine import engine

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

    def execute(
        self,
        input_entity: Entity,
        text: str,
        _engine: Optional[engine.ActionEngine] = None,
    ) -> Entity:
        if getattr(input_entity, "entity_type", None) not in ENTITY_TYPES:
            raise ValueError(
                f"Cannot comment on {input_entity}, expected a folder, task, "
                "product or version."
            )
        if not text or not text.strip():
            raise ValueError("No comment text.")
        activity_id = ayon_api.create_activity(
            input_entity.project_name,
            input_entity.id,
            input_entity.entity_type,
            "comment",
            body=text,
        )
        self.inject_custom_backend_data(_engine, activity_id=activity_id)
        return input_entity

    def revert_execute(
        self,
        input_entity: Entity,
        text: str,
        _custom_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        activity_id = (_custom_data or {}).get("activity_id")
        if activity_id:
            ayon_api.delete_activity(input_entity.project_name, activity_id)
