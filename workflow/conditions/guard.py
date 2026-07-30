from typing import Any, Union, Optional

import contextlib

from taskflow import states

from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)
from ayon_workflow.workflow_execution.from_backend import dir_backend



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
            name="result",
            description="The result of the guard.",
        )
    ]

    def execute(
            self,
            input_data: Any,
            condition: Union[bool, str, None] = None,
            _engine = None,
            _backend_directory: Optional[str] = None,
            _main_flow_id: Optional[str] = None,
    ) -> Any:
        if condition is None:
            result = bool(input_data)
        elif isinstance(condition, str):
            result = eval(condition)
        else:
            result = bool(condition)

        if not result:
            # Stop the execution of current engine.
            if _engine is not None:
                _engine.suspend()

            # Execution is run from a backend,
            # flag all remaining atoms as IGNORED.
            if _backend_directory and _main_flow_id:
                _set_atoms_in_backend_as_ignored(
                    _backend_directory,
                    _main_flow_id
                )

        return input_data


def _set_atoms_in_backend_as_ignored(
    backend_directory: str,
    main_flow_id: str,
):
    backend, _ = dir_backend.get_backend(
        temp_dir=backend_directory,
        validate=True,
    )

    with contextlib.closing(backend.get_connection()) as conn:
        logbook = conn.get_logbook(dir_backend.LOGBOOK_NAME)
        main_flow_details = logbook.find(main_flow_id)
        for atom_detail in conn.get_atoms_for_flow(main_flow_details.uuid):
            if atom_detail.state != states.PENDING:
                continue

            atom_detail.state = states.IGNORE
            atom_detail.intention = states.IGNORE
            conn.update_atom_details(atom_detail)
