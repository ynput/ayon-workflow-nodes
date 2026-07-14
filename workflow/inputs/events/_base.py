from typing import Optional, Any, Dict

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
    event_type: Optional[str] = None
    inputs = [
        InputAttribute(
            name="event_id",
            description="An input data to be injected as-is.",
        )
    ]

    def __init__(
        self,
        name: Optional[str] = None,
        provides: Optional[list[str]] = None,
        inject: Optional[dict[str, Any]] = None,
        rebind: Optional[dict[str, str]] = None,
    ):
        if self.event_type is None:
            log.warning(
                f"Event trigger class {self.__class__.__name__} does not "
                "define event type. It is required for the event processor."
            )

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
