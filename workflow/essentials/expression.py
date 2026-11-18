from typing import Any

from ayon_workflow.datatypes import Entity
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from . import _utils


# what an expression can call, nothing that reaches files or imports
SAFE_BUILTINS = {
    function.__name__: function
    for function in (
        abs, all, any, bool, float, int, len, max, min, round, sorted, str,
        sum,
    )
}


class Expression(WorkflowTaskNode):
    """Compute a value with a Python expression, for example from the
    attributes of an AYON entity."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_data",
            description=(
                "The data, a list when several outputs are connected. For a "
                "folder, task, product or version, its attributes are in "
                "`attrib`."
            ),
            allow_multi_connection=True,
        ),
        InputAttribute(
            name="expression",
            description=(
                "A Python expression on `input_data` and `attrib`, for "
                'example attrib["frameStart"] + 100 (trusted workflows '
                "only)."
            ),
            widget={"name": "python_code"},
        ),
    ]
    outputs = [
        OutputAttribute(
            name="result",
            description="The value of the expression.",
        )
    ]

    def execute(self, input_data: Any, expression: str) -> Any:
        if not expression:
            raise ValueError("No expression to compute.")
        attrib = {}
        if isinstance(input_data, Entity):
            attrib = _utils.get_entity_data(
                input_data, fields={"attrib"}
            ).get("attrib") or {}
        return eval(
            expression,
            {"__builtins__": SAFE_BUILTINS},
            {"input_data": input_data, "attrib": attrib},
        )
