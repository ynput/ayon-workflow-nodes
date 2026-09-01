from typing import Optional, Tuple, List


from ayon_workflow.datatypes import TaskItem
from ayon_workflow.plugin_system import (
    OutputAttribute,
)

from ayon_workflow.plugins.workflow.essentials import _utils
from .base import EventTrigger


class OnTaskAssigneesChanged(EventTrigger):
    """Trigger node: on task assignees changed."""

    version = "0.0.1"
    event_type = "entity.task.assignees_changed"
    outputs = [
        OutputAttribute(
            name="event_context",
            description="The output event task context.",
        ),
        OutputAttribute(
            name="event_assignees",
            description="The output event task assginees.",
        )
    ]

    def execute(
        self,
        event_id: Optional[str] = None
    ) -> Tuple[Optional[TaskItem], Optional[List[str]]]:
        """ Return the task context and assignees associated to the event.
        """
        if event_id is None:
            return None, None

        event_data = super().execute(event_id)
        entity_path = event_data["summary"]["entityPath"]
        folder_path, task_name = entity_path.rsplit("/", 1)
        folder_item = _utils.get_folder_item(
            event_data["project"],
            folder_path=folder_path,
        )
        task_item = _utils.get_task_item(
            event_data["project"],
            folder_item,
            task_name=task_name,
        )

        return (
            task_item,
            event_data["summary"]["value"],
        )
