from typing import Optional, Tuple

import ayon_api

from ayon_workflow.datatypes import (
    FolderItem,
    ProductItem,
    VersionItem,
)
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
)

from ayon_workflow.plugins.workflow.essentials import _utils
from ..base import EventTrigger

class OnActionFromVersion(EventTrigger):
    """Trigger node: on simple action from version."""

    version = "0.0.1"
    event_topic = [
        "workflow.from_simple_action.local",
        "workflow.from_simple_action.remote",
    ]
    inputs = [
        InputAttribute(
            name="project_name",
            description="The project name.",
        ),
        InputAttribute(
            name="entity_id",
            description="The entity ID.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="event_context",
            description="The output event context.",
        ),
        OutputAttribute(
            name="event_version",
            description="The output event version.",
        )
    ]

    def execute(
        self,
        project_name: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> Tuple[Optional[FolderItem], Optional[VersionItem]]:
        """ Return the context and version associated to the simple action.
        """
        if (
            project_name is None
            or entity_id is None
        ):
            return None, None

        version_data = ayon_api.get_version_by_id(
            project_name,
            entity_id
        )
        product_data = ayon_api.get_product_by_id(
            project_name,
            version_data["productId"],
        )
        folder_item = _utils.get_folder_item(
            project_name,
            folder_id=product_data["folderId"],
        )

        return (
            folder_item,
            VersionItem(
                version_id=entity_id,
                product=ProductItem(
                    product_id=product_data["id"],
                    folder=folder_item,
                ),
                version=version_data["version"],
            )
        )
