from typing import Any, Optional

import contextlib

from taskflow import states
from taskflow.engines.action_engine import engine

from ayon_workflow.workflow_execution.from_backend import dir_backend


def evaluate_condition(condition: Any, input_data: Any) -> bool:
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

    return result


def ignore_pending_atoms_in_engine(
    engine: engine.ActionEngine,
    atom_names: Optional[list[str]] = None,
):
    """ Flag atom from current engine as state.IGNORE.
    """
    # Default to all nodes.
    if atom_names is None:
        atom_names = [atom.name for atom in engine._flow]

    atom_states = engine.storage.get_atoms_states(atom_names)
    for name, (state, _) in atom_states.items():
        if state == states.PENDING:
            engine.storage.set_atom_state(name, states.IGNORE)
            engine.storage.set_atom_intention(name, states.IGNORE)


def ignore_pending_atoms_in_backend(
    backend_directory: str,
    main_flow_id: str,
    atom_names: Optional[list[str]] = None,
):
    """ Flag atom from backend as state.IGNORE.
    """
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
            if atom_names and atom_detail.name not in atom_names:
                continue

            if atom_detail.state != states.PENDING:
                continue

            atom_detail.state = states.IGNORE
            atom_detail.intention = states.IGNORE
            conn.update_atom_details(atom_detail)
