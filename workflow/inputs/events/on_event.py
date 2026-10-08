from typing import Any, Dict, List, Optional, Tuple, Union

from ayon_workflow.datatypes import Entity
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    SkipWorkflowInput,
    WorkflowConditionTaskNode,
)

from ayon_workflow.plugins.workflow.essentials import _utils
from .base import EventTrigger


ENTITY_TYPES = ("folder", "task", "product", "version")


def _topics(value: Union[str, List[str], None]) -> List[str]:
    if isinstance(value, str):
        value = value.split(",")
    return [topic.strip() for topic in value or [] if topic.strip()]


class OnEvent(EventTrigger):
    """Trigger node: when an AYON event of the given topic happens,
    optionally only when a condition on the event holds."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="event_id",
            description="The id of the event to inject.",
        ),
        InputAttribute(
            name="topic",
            description=(
                "The event topic, for example entity.task.created. Several "
                "topics separated by commas."
            ),
        ),
        InputAttribute(
            name="condition",
            description=(
                "Only when this Python expression on `input_data`, the event "
                "(topic, summary, payload, user...), is true. Always when "
                "empty (trusted workflows only)."
            ),
        ),
    ]
    outputs = [
        OutputAttribute(
            name="entity",
            description=(
                "The folder, task, product or version of an entity.* event."
            ),
        ),
        OutputAttribute(
            name="event",
            description="The event: topic, summary, payload, user...",
        ),
    ]

    @classmethod
    def get_event_topics(cls, execute_values: Dict[str, Any]) -> List[str]:
        return _topics(execute_values.get("topic"))

    def execute(
        self,
        event_id: Optional[str] = None,
        topic: Optional[str] = None,
        condition: Optional[str] = None,
    ) -> Tuple[Optional[Entity], Optional[Dict[str, Any]]]:
        """ Return the entity of the event and the event, or skip the rest
        of the workflow when the condition does not hold.
        """
        if event_id is None:
            return None, None

        event_data = super().execute(event_id)
        if condition and not WorkflowConditionTaskNode.evaluate_condition(
            condition, input_data=event_data
        ):
            raise SkipWorkflowInput(f"{condition} is false for this event")

        entity = None
        parts = event_data["topic"].split(".")
        entity_id = (event_data.get("summary") or {}).get("entityId")
        if (
            len(parts) > 2
            and parts[0] == "entity"
            and parts[1] in ENTITY_TYPES
            and entity_id
            and event_data.get("project")
        ):
            entity = _utils.get_entity_item(
                event_data["project"], parts[1], entity_id
            )
        return entity, event_data
