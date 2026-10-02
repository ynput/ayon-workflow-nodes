from typing import Any, Dict, Optional, Tuple

from ayon_workflow.datatypes import Entity
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
)

from ayon_workflow.plugins.workflow.essentials import _utils
from .base import EventTrigger


ENTITY_TYPES = ("folder", "task", "product", "version")
ANY = "any"


def _matches(wanted: Optional[str], value: Optional[str]) -> bool:
    """ An empty filter (or "any") takes everything, without case. """
    if not wanted or wanted.strip().lower() == ANY:
        return True
    return (value or "").lower() == wanted.strip().lower()


class OnStatusChanged(EventTrigger):
    """Trigger node: when the status of a folder, task, product or version
    changes, optionally only for one entity type or certain statuses."""

    version = "0.0.1"
    event_topic = [f"entity.{name}.status_changed" for name in ENTITY_TYPES]
    inputs = [
        InputAttribute(
            name="event_id",
            description="The id of the event to inject.",
        ),
        InputAttribute(
            name="entity_type",
            description="Only for this entity type.",
            default=ANY,
            widget={"name": "choice", "options": [ANY, *ENTITY_TYPES]},
        ),
        InputAttribute(
            name="to_status",
            description=(
                "Only when the new status is this one (not case sensitive), "
                "any status when empty."
            ),
            default="",
            widget={"name": "status"},
        ),
        InputAttribute(
            name="from_status",
            description=(
                "Only when the status was this one before, any status when "
                "empty."
            ),
            default="",
            widget={"name": "status"},
        ),
    ]
    outputs = [
        OutputAttribute(
            name="entity",
            description="The folder, task, product or version.",
        ),
        OutputAttribute(
            name="new_status",
            description="Its status now.",
        ),
        OutputAttribute(
            name="old_status",
            description="Its status before.",
        ),
    ]

    @classmethod
    def accepts_event(
        cls,
        event: Dict[str, Any],
        values: Dict[str, Any],
    ) -> bool:
        payload = event.get("payload") or {}
        return (
            _matches(values.get("entity_type"), event["topic"].split(".")[1])
            and _matches(values.get("to_status"), payload.get("newValue"))
            and _matches(values.get("from_status"), payload.get("oldValue"))
        )

    def execute(
        self,
        event_id: Optional[str] = None,
        entity_type: str = ANY,
        to_status: str = "",
        from_status: str = "",
    ) -> Tuple[Optional[Entity], Optional[str], Optional[str]]:
        """ Return the entity and its new and old status.
        """
        if event_id is None:
            return None, None, None

        event_data = super().execute(event_id)
        payload = event_data.get("payload") or {}
        entity = _utils.get_entity_item(
            event_data["project"],
            event_data["topic"].split(".")[1],
            event_data["summary"]["entityId"],
        )
        return entity, payload.get("newValue"), payload.get("oldValue")
