from typing import Optional, Any, Dict, List, Union

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
    event_topic: Union[str, List[str], None] = None
    inputs = [
        InputAttribute(
            name="event_id",
            description="The id of the event to inject.",
        )
    ]

    def __init__(
        self,
        name: Optional[str] = None,
        provides: Optional[list[str]] = None,
        inject: Optional[dict[str, Any]] = None,
        rebind: Optional[dict[str, str]] = None,
    ):
        if not self.event_topic:
            log.warning(
                f"Event trigger class {self.__class__.__name__} does not "
                "define event topic. It is required for the event processor."
            )

        super().__init__(
            name=name,
            provides=provides,
            inject=inject,
            rebind=rebind,
        )

    @classmethod
    def accepts_event(
        cls,
        event: Dict[str, Any],
        values: Dict[str, Any],
    ) -> bool:
        """ Whether the workflow runs for this event, decided from the event
        and the static values of the trigger node (its filters).

        The event processor asks before it starts (and records) a run, so a
        workflow can react to some events of a topic only.
        """
        return True

    def execute(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        """ Return the event data.
        """
        if event_id is None:
            return {}

        return ayon_api.get_event(event_id)
