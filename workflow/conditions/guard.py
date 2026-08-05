from typing import Any, Union, Optional

from taskflow.engines.action_engine import engine

from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)
from ayon_workflow.plugins.workflow.conditions import _utils


class Guard(WorkflowTaskNode):
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
        OutputAttribute(
            name="output_data",
            description="The result of the guard.",
        )
    ]

    def execute(
            self,
            input_data: Any,
            condition: Union[bool, str, None] = None,
            _engine: Optional[engine.ActionEngine] = None,
            _backend_directory: Optional[str] = None,
            _main_flow_id: Optional[str] = None,
    ) -> Any:
        if not _utils.evaluate_condition(condition, input_data):
            # flag all remaining atoms from current flow as IGNORED.
            if _engine is not None:
                _utils.ignore_pending_atoms_in_engine(_engine)
                _engine.suspend()

            # If execution is run from a backend, flag all
            # remaining atoms from other flows as IGNORED.
            if _backend_directory and _main_flow_id:
                _utils.ignore_pending_atoms_in_backend(
                    _backend_directory,
                    _main_flow_id
                )

        return input_data
