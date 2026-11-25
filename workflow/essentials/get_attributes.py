from typing import Any, Dict

from ayon_workflow.datatypes import Entity
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from . import _utils


class GetAttributes(WorkflowTaskNode):
    """Get the attributes of an AYON folder, task, product or version."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_entity",
            description="The folder, task, product or version.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="attributes",
            description="Its attributes by name, inherited ones included.",
        )
    ]

    def execute(self, input_entity: Entity) -> Dict[str, Any]:
        data = _utils.get_entity_data(input_entity, fields={"attrib"})
        return data.get("attrib") or {}
