from typing import Union

import ayon_api

from ayon_workflow.datatypes import (
    Entity,
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
            name="input_entity",
            description="An AYON entity.",
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
            name="edited_entity",
            description="The entity with watchers set.",
        )
    ]

    def execute(
        self,
        input_entity: Entity,
        watchers: Union[str, list[str]],
        edit_mode: str = "add",
    ) -> Entity:
        if isinstance(watchers, str):
            watchers = [watchers]

        if edit_mode not in self.EDIT_MODES:
            raise ValueError(
                f"Invalid edit mode: {edit_mode}, "
                f"must be one of {self.EDIT_MODES}"
            )

        if edit_mode in ("add", "remove", "toggle"):
            existing_watchers = ayon_api.get_entity_watchers(
                input_entity.project_name,
                input_entity.id,
                input_entity.entity_type,
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
            input_entity.project_name,
            input_entity.id,
            input_entity.entity_type,
            watchers,
        )

        return input_entity
