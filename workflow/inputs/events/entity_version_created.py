from typing import Optional, Tuple

import ayon_api

from ayon_workflow.datatypes import (
    ContextItem,
    ProjectItem,
    VersionItem,
)
from ayon_workflow.plugin_system import (
    OutputAttribute,
)
from .base import EventTrigger


class OnVersionCreated(EventTrigger):
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
        version_data = ayon_api.get_version_by_id(
            event_data["project"],
            event_data["summary"]["entityId"],
        )

        return (
            ProjectItem(
                project_name=event_data["project"],
                # return folder associated to the product ?
            ),
            VersionItem(
                version_id=event_data["summary"]["entityId"],
                product_id=event_data["summary"]["parentId"],
                version=version_data["version"],
            )
        )
