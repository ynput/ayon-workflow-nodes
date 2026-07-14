from typing import Any

from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowInputTaskNode,
)


class GenericInput(WorkflowInputTaskNode):
    """A generic input node that inject input data as-is."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_data",
            description="An input data to be injected as-is.",
        )
    ]
    outputs = [
        OutputAttribute(
            name="output_data",
            description="The input data injected as-is.",
        )
    ]

    def execute(self, input_data: Any) -> Any:
        """ Return the input data as-is.
        """
        return input_data
