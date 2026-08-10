from typing import Any, Union, Optional

from taskflow.engines.action_engine import engine

from ayon_workflow.plugin_system import (
    InputAttribute,
    ConditionOutputAttribute,
    WorkflowConditionTaskNode,
)


class Guard(WorkflowConditionTaskNode):
    """Stop properly a workflow based on a condition."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_data",
            description="The input data.",
        ),
        InputAttribute(
            name="condition",
            description=(
                "The condition to evaluate. "
                "Defaults to bool(input_data)."
            ),
        ),
    ]
    outputs = [
        ConditionOutputAttribute(
            name="output_data",
            description="The result of the guard when condition is met.",
        )
    ]

    def execute(
            self,
            input_data: Any,
            condition: Union[bool, str, None] = True,
            _engine: Optional[engine.ActionEngine] = None,
            _backend_directory: Optional[str] = None,
            _main_flow_id: Optional[str] = None,
    ) -> Any:
        result = self.evaluate_condition(condition, input_data=input_data)

        # Skip all pending task if condition is not met.
        if not result:
            self.skip_output(
                _engine=_engine,
                _backend_directory=_backend_directory,
                _main_flow_id=_main_flow_id,
            )

        return input_data
