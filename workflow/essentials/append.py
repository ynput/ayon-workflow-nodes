from typing import Any, List, Union

from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class Append(WorkflowTaskNode):
    """Group or Append inputs as a list."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="inputs",
            description="Any input(s).",
            allow_multi_connection=True,
        )
    ]
    outputs = [
        OutputAttribute(
            name="appended_data",
            description="The appended data as a list.",
        )
    ]

    def execute(self, inputs: Union[Any, List[Any]]) -> List[Any]:
        result = []
        for input in inputs:
            if isinstance(input, list):
                result.extend(input)
            else:
                result.append(input)
        return result
