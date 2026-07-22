from typing import Optional

from ayon_workflow.datatypes import (
    ContextItem,
)
from ayon_workflow.plugin_system import (
    OutputAttribute,
)
from ..base import EventTrigger


class ActionFromFolder(EventTrigger):
    """Trigger node: on simple action from folder."""

    version = "0.0.1"
    event_type = [
        "workflow.from_simple_action.local",
        "workflow.from_simple_action.remote",
    ]
    outputs = [
        OutputAttribute(
            name="event_context",
            description="The output event context.",
        )
    ]

    def execute(
        self,
        event_id: Optional[str] = None
    ) -> Optional[ContextItem]:
        """ Return the context item associated to the simple action.
        """
        if event_id is None:
            return None

        event_data = super().execute(event_id)
        return ContextItem(
            project_name=event_data["project"],
            # TODO: fill up folderId from provided event_id
            #folder_id=...
        )
