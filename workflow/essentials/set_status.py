from typing import Optional

import ayon_api

from ayon_workflow.datatypes import (
    Entity,
)
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


def _get_status_names(project_name: str, entity_type: str) -> list[str]:
    """ Statuses of the project anatomy that apply to an entity type.
    """
    project = ayon_api.get_project(project_name) or {}
    return [
        status["name"]
        for status in project.get("statuses") or []
        # no scope means every entity type
        if not status.get("scope") or entity_type in status["scope"]
    ]


def _get_status(entity: Entity) -> Optional[str]:
    getter = {
        "folder": ayon_api.get_folder_by_id,
        "task": ayon_api.get_task_by_id,
        "product": ayon_api.get_product_by_id,
        "version": ayon_api.get_version_by_id,
    }[entity.entity_type]
    data = getter(entity.project_name, entity.id, fields={"status"}) or {}
    return data.get("status")


def _update_status(entity: Entity, status: str):
    update = {
        "folder": ayon_api.update_folder,
        "task": ayon_api.update_task,
        "product": ayon_api.update_product,
        "version": ayon_api.update_version,
    }[entity.entity_type]
    update(entity.project_name, entity.id, status=status)


class SetStatus(WorkflowTaskNode):
    """Set the status of an AYON folder, task, product or version."""

    ENTITY_TYPES = ("folder", "task", "product", "version")

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_entity",
            description="The folder, task, product or version to change.",
        ),
        InputAttribute(
            name="status",
            description=(
                "The status to set, one of the project statuses for this "
                "entity type (not case sensitive)."
            ),
        ),
    ]
    outputs = [
        OutputAttribute(
            name="edited_entity",
            description="The entity with its status set.",
        )
    ]

    def execute(self, input_entity: Entity, status: str) -> Entity:
        self._previous_status = None
        entity_type = getattr(input_entity, "entity_type", None)
        if entity_type not in self.ENTITY_TYPES:
            raise ValueError(
                f"Cannot set the status of {input_entity}, expected one of "
                f"{', '.join(self.ENTITY_TYPES)}."
            )
        if not status:
            raise ValueError("No status to set.")

        names = _get_status_names(input_entity.project_name, entity_type)
        matches = [name for name in names if name.lower() == status.lower()]
        if not matches:
            raise ValueError(
                f"{status!r} is not a {entity_type} status in project "
                f"{input_entity.project_name}. "
                f"Expected one of: {', '.join(names)}."
            )

        # Store previous value to restore it in revert if needed
        self._previous_status = _get_status(input_entity)
        _update_status(input_entity, matches[0])
        return input_entity

    def revert_execute(
        self,
        input_entity: Entity,
        status: str,
        **kwargs,
    ):
        previous = getattr(self, "_previous_status", None)
        if previous:
            _update_status(input_entity, previous)
