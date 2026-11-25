from typing import Optional, Dict, Any, List

from ayon_workflow.datatypes import (
    ContextItem,
)
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
)

from ayon_workflow.plugins.workflow.essentials import _utils
from ..base import EventTrigger

class OnActionFromFolder(EventTrigger):
    """Trigger node: on simple action from folder."""

    version = "0.0.1"
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
        )
    ]

    @classmethod
    def get_event_topics(cls, execute_values: Dict[str, Any]) -> List[str]:
        return [
            "workflow.from_simple_action.local",
            "workflow.from_simple_action.remote",
        ]

    def execute(
        self,
        project_name: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> Optional[ContextItem]:
        """ Return the context item associated to the simple action.
        """
        if (
            project_name is None
            or entity_id is None
        ):
            return None

        return _utils.get_folder_item(
            project_name,
            folder_id=entity_id,
        )
