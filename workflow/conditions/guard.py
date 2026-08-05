from typing import Any, Union, Optional

import contextlib

from taskflow import states
from taskflow.engines.action_engine import engine

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
            name="output_data",
            description="The result of the guard.",
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
        if condition is None:
            result = bool(input_data)
        elif isinstance(condition, str):
            result = bool(eval(
                condition,
                {"__builtins__": {}},
                {"input_data": input_data},
            ))
        else:
            result = bool(condition)

        if not result:
            # flag all remaining atoms from current flow as IGNORED.
            if _engine is not None:
                _set_engine_atoms_as_ignored(_engine)
                _engine.suspend()

            # If execution is run from a backend, flag all
            # remaining atoms from other flows as IGNORED.
            if _backend_directory and _main_flow_id:
                _set_other_atoms_in_backend_as_ignored(
                    _backend_directory,
                    _main_flow_id
                )

        return input_data


def _set_engine_atoms_as_ignored(engine):
    atom_names = [atom.name for atom in engine._flow]
    atom_states = engine.storage.get_atoms_states(atom_names)
    for name, (state, _) in atom_states.items():
        if state == states.PENDING:
            engine.storage.set_atom_state(name, states.IGNORE)
            engine.storage.set_atom_intention(name, states.IGNORE)


def _set_other_atoms_in_backend_as_ignored(
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
        if main_flow_details is None:
            raise RuntimeError(
                f"Cannot find main flow {main_flow_id} "
                f"in backend directory: {backend_directory}"
            )

        for atom_detail in conn.get_atoms_for_flow(main_flow_details.uuid):
            if atom_detail.state != states.PENDING:
                continue

            atom_detail.state = states.IGNORE
            atom_detail.intention = states.IGNORE
            conn.update_atom_details(atom_detail)
