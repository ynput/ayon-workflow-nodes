from typing import Any

from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class Display(WorkflowTaskNode):
    """Show the incoming value in the editor once executed.

    The value is passed through unchanged, so the node can be inserted
    anywhere in a chain to inspect the data flowing through it.
    """

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="value",
            description="The value to display.",
        )
    ]
    outputs = [
        OutputAttribute(
            name="output",
            description="The input value, unchanged.",
        )
    ]
    # Editor hint: render the last produced value in the node body.
    ui = {"style": "display", "value_output": "output"}

    def execute(self, value: Any = None) -> Any:
        """ Return the value as-is.
        """
        return value
