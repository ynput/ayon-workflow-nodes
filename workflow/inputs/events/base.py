from typing import Optional, Any, Dict, List


import ayon_api

from ayon_workflow.plugin_system import (
    WorkflowInputTaskNode,
    InputAttribute,
)


class EventTrigger(WorkflowInputTaskNode):
    """A base class for event trigger node."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="event_id",
            description="The id of the event to inject.",
        )
    ]

    @classmethod
    def get_event_topics(cls, execute_values: Dict[str, Any]) -> List[str]:
        """ Return the event topic associated to the EventTrigger,
            can use values provided to execute() as execute_values.
            Must be overwritten per input node.
        """
        return []

    def execute(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        """ Return the event data.
        """
        if event_id is None:
            return {}

        return ayon_api.get_event(event_id)
