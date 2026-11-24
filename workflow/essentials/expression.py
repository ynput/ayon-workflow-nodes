from typing import Any

from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


# what an expression can call, nothing that reaches files or imports
SAFE_BUILTINS = {
    function.__name__: function
    for function in (
        abs, all, any, bool, float, int, len, max, min, round, sorted, str,
        sum,
    )
}


class Expression(WorkflowTaskNode):
    """Compute a value with a Python expression."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_data",
            description="The data.",
        ),
        InputAttribute(
            name="expression",
            description=(
                "A Python expression on `input_data`."
                "It runs as Python code on the runner: "
                "anyone who can publish this workflow can run it."
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
        return eval(
            expression,
            {"__builtins__": SAFE_BUILTINS},
            {"input_data": input_data},
        )
