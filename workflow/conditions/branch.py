from typing import Any, Union, Optional, Tuple

from taskflow.engines.action_engine import engine

from ayon_workflow.plugin_system import (
    InputAttribute,
    ConditionOutputAttribute,
    WorkflowConditionTaskNode,
)


class Branch(WorkflowConditionTaskNode):
    """Branch workflow execution based on a condition."""

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
            name="on_True",
            description="input_data when condition is True",
        ),
        ConditionOutputAttribute(
            name="on_False",
            description="input_data when condition is False",
        )
    ]

    def execute(
            self,
            input_data: Any,
            condition: Union[bool, str, None] = None,
            _engine: Optional[engine.ActionEngine] = None,
            _backend_directory: Optional[str] = None,
            _main_flow_id: Optional[str] = None,
    ) -> Tuple[Any, Any]:
        if self.evaluate_condition(condition, input_data=input_data):
            ignored_output = list(self.provides)[1]
            result = input_data, None
        else:
            ignored_output = list(self.provides)[0]
            result = None, input_data

        # Ignore downstream task(s) connected to ignored output.
        self.skip_output(
            output_name=ignored_output,
            _engine=_engine,
            _backend_directory=_backend_directory,
            _main_flow_id=_main_flow_id,
        )
        return result
