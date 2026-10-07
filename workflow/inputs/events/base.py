from typing import Any, Dict, List, Optional, Union

import ayon_api

from ayon_workflow.plugin_system import (
    WorkflowInputTaskNode,
    InputAttribute,
)


class EventTrigger(WorkflowInputTaskNode):
    """A base class for event trigger node."""

    version = "0.0.1"
    event_topic: Union[str, List[str], None] = None
    inputs = [
        InputAttribute(
            name="event_id",
            description="The id of the event to inject.",
        )
    ]

    @classmethod
    def event_topics(cls, values: Dict[str, Any]) -> List[str]:
        """ The topics the event processor registers the workflow on, from
        the static values of the trigger node. `event_topic` by default.
        """
        if isinstance(cls.event_topic, str):
            return [cls.event_topic]
        return list(cls.event_topic or [])

    def execute(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        """ Return the event data.
        """
        if event_id is None:
            return {}

        return ayon_api.get_event(event_id)
