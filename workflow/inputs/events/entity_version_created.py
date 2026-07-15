from typing import Optional, Tuple

from ayon_workflow.datatypes import (
    ContextItem,
    VersionItem,
)
from ayon_workflow.plugin_system import (
    OutputAttribute,
)
from .base import EventTrigger


class EntityVersionCreated(EventTrigger):
    """Trigger node: on new version created."""

    version = "0.0.1"
    event_type = "entity.version.created"
    outputs = [
        OutputAttribute(
            name="event_context",
            description="The output event context.",
        ),
        OutputAttribute(
            name="event_version_item",
            description="The output version item.",
        )
    ]

    def execute(
        self,
        event_id: Optional[str] = None
    ) -> Tuple[Optional[ContextItem], Optional[VersionItem]]:
        """ Return the context and version item associated to the event.
        """
        if event_id is None:
            return None, None

        event_data = super().execute(event_id)
        return (
            ContextItem(
                project_name=event_data["project"],
                # TODO: return folder associated instead of version item
            ),
            VersionItem(
                version_id=event_data["summary"]["entityId"],
                product_id=event_data["summary"]["parentId"],
                version=None
            )
        )
