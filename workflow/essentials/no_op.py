from typing import Any

from ayon_workflow.plugin_system.interface import WorkflowNode


class NoOp(WorkflowNode):
    """Return input as-is (no operation)."""

    version = "0.0.1"
    inputs = {
        "input_data": {
            "description": "An input data to be returned as-is.",
        }
    }
    outputs = {
        "output_data": {
            "description": "The input data returned as-is.",
        }
    }

    def execute(self, input_data: Any) -> Any:
        """ Return the input data as-is.
        """
        return input_data
