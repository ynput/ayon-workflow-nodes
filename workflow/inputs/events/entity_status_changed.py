from typing import Any, Dict, List, Optional, Tuple

from ayon_workflow.datatypes import Entity
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    SkipWorkflowInput,
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
    inputs = [
        InputAttribute(
            name="event_id",
            description="The id of the event to inject.",
        ),
        InputAttribute(
            name="entity_type",
            description="Only for this entity type.",
            widget={"name": "choice", "options": [ANY, *ENTITY_TYPES]},
        ),
        InputAttribute(
            name="to_status",
            description=(
                "Only when the new status is this one (not case sensitive), "
                "any status when empty."
            ),
            widget={"name": "status"},
        ),
        InputAttribute(
            name="from_status",
            description=(
                "Only when the status was this one before, any status when "
                "empty."
            ),
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
    def get_event_topics(cls, execute_values: Dict[str, Any]) -> List[str]:
        entity_type = (execute_values.get("entity_type") or "").strip().lower()
        if entity_type in ENTITY_TYPES:
            return [f"entity.{entity_type}.status_changed"]
        return [f"entity.{name}.status_changed" for name in ENTITY_TYPES]

    def execute(
        self,
        event_id: Optional[str] = None,
        entity_type: str = ANY,
        to_status: str = "",
        from_status: str = "",
    ) -> Tuple[Optional[Entity], Optional[str], Optional[str]]:
        """ Return the entity and its new and old status, or skip the rest
        of the workflow when the change does not match the filters.
        """
        if event_id is None:
            return None, None, None

        event_data = super().execute(event_id)
        changed_type = event_data["topic"].split(".")[1]
        payload = event_data.get("payload") or {}
        new_status = payload.get("newValue")
        old_status = payload.get("oldValue")

        mismatch = None
        if not _matches(entity_type, changed_type):
            mismatch = f"a {changed_type} changed, not a {entity_type}"
        elif not _matches(to_status, new_status):
            mismatch = f"the new status is {new_status}, not {to_status}"
        elif not _matches(from_status, old_status):
            mismatch = f"the status was {old_status}, not {from_status}"
        if mismatch:
            raise SkipWorkflowInput(mismatch)

        entity = _utils.get_entity_item(
            event_data["project"],
            changed_type,
            event_data["summary"]["entityId"],
        )
        return entity, new_status, old_status
