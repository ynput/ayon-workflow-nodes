from typing import Any, Dict, List, Optional, Union

import ayon_api
from taskflow.engines.action_engine import engine

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
        if status.get("scope") is None or entity_type in status["scope"]
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
    """Set the status of AYON folders, tasks, products or versions."""

    ENTITY_TYPES = ("folder", "task", "product", "version")

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_entity",
            description=(
                "The folder, task, product or version to change, "
                "or a list of them."
            ),
            allow_multi_connection=True,
        ),
        InputAttribute(
            name="status",
            description=(
                "The status to set, one of the project statuses for this "
                "entity type (not case sensitive)."
            ),
            widget={"name": "status"},
        ),
    ]
    outputs = [
        OutputAttribute(
            name="edited_entity",
            description="The entity, or the list, with the status set.",
        )
    ]

    def execute(
        self,
        input_entity: Union[Entity, List[Entity]],
        status: str,
        _engine: Optional[engine.ActionEngine] = None,
    ) -> Union[Entity, List[Entity]]:
        if not status:
            raise ValueError("No provided status to set.")

        if isinstance(input_entity, list):
            entities = input_entity
        else:
            entities = [input_entity]

        new_statuses = []
        status_names_by_type = {}
        for entity in entities:

            # Check supported entity.
            entity_type = getattr(entity, "entity_type", None)
            if entity_type not in self.ENTITY_TYPES:
                raise ValueError(
                    f"Unsupported entity: {entity}, expected one of "
                    f"{', '.join(self.ENTITY_TYPES)}."
                )

            # Find and validate new status.
            key = (entity.project_name, entity_type)
            if key not in status_names_by_type:
                status_names_by_type[key] = _get_status_names(*key)

            names = status_names_by_type[key]
            matches = [
                name
                for name in names
                if name.lower() == status.lower()
            ]
            if not matches:
                raise ValueError(
                    f"{status!r} is not a {entity_type} status in project "
                    f"{entity.project_name}. "
                    f"Expected one of: {', '.join(names)}."
                )
            new_statuses.append(matches[0])

        previous_statuses = []
        try:
            for entity, new in zip(entities, new_statuses):
                previous = _get_status(entity)
                # skip update if no change, optimization but
                # also do not emit events (prevent workflow loop)
                if previous == new:
                    previous = None  # no need to revert
                else:
                    _update_status(entity, new)
                previous_statuses.append(previous)
        finally:
            self.inject_custom_backend_data(
                _engine, previous_statuses=previous_statuses
            )

        return input_entity

    def revert_execute(
        self,
        input_entity: Union[Entity, List[Entity]],
        status: str,
        _custom_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        if isinstance(input_entity, list):
            entities = input_entity
        else:
            entities = [input_entity]

        previous_statuses = (_custom_data or {}).get("previous_statuses", [])
        for entity, previous in zip(entities, previous_statuses):
            if previous:
                _update_status(entity, previous)
