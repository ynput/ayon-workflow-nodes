from typing import Any, List, Union

from ayon_workflow.plugin_system.interface import WorkflowNode


class Append(WorkflowNode):
    """Group or Append inputs as a list."""

    version = "0.0.1"
    inputs = {
        "inputs": {
            "description": "Any input(s).",
            "allow_multi_connection": True,
        }
    }
    outputs = {
        "appended_data": {
            "description": "The appended data as a list.",
        }
    }

    def execute(self, inputs: Union[Any, List[Any]]) -> List[Any]:
        result = []
        for input in inputs:
            if isinstance(input, list):
                result.extend(input)
            else:
                result.append(input)
        return result
