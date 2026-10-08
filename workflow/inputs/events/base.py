from typing import Optional, Any, Dict, List

import logging

import ayon_api

from ayon_workflow.plugin_system import (
    WorkflowInputTaskNode,
    InputAttribute,
)


log = logging.getLogger(__name__)


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

    def __init__(
        self,
        name: Optional[str] = None,
        provides: Optional[list[str]] = None,
        inject: Optional[dict[str, Any]] = None,
        rebind: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            name=name,
            provides=provides,
            inject=inject,
            rebind=rebind,
        )

    def execute(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        """ Return the event data.
        """
        if event_id is None:
            return {}

        return ayon_api.get_event(event_id)
