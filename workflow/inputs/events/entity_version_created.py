from typing import Optional, Tuple

import ayon_api

from ayon_workflow.datatypes import (
    FolderItem,
    VersionItem,
)
from ayon_workflow.plugin_system import (
    OutputAttribute,
)

from ayon_workflow.plugins.workflow.essentials import _utils
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
    ) -> Tuple[Optional[FolderItem], Optional[VersionItem]]:
        """ Return the context and version item associated to the event.
        """
        if event_id is None:
            return None, None

        event_data = super().execute(event_id)
        version_data = ayon_api.get_version_by_id(
            event_data["project"],
            event_data["summary"]["entityId"],
        )
        product_data = ayon_api.get_product_by_id(
            event_data["project"],
            version_data["productId"],
        )
        folder_item = _utils.get_folder_item(
            event_data["project"],
            folder_id=product_data["folderId"],
        )

        return (
            folder_item,
            VersionItem(
                version_id=event_data["summary"]["entityId"],
                product_id=event_data["summary"]["parentId"],
                version=version_data["version"],
            )
        )
