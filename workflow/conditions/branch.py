from typing import Any, Union, Optional, Tuple, List, Dict

import contextlib

from taskflow import flow
from taskflow.engines.action_engine import engine

from ayon_workflow.plugin_system import (
    WorkflowNode,
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)
from ayon_workflow.workflow_execution.from_backend import dir_backend
from ayon_workflow.plugins.workflow.conditions import _utils


class Branch(WorkflowTaskNode):
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
        OutputAttribute(
            name="on_True",
            description="input_data when condition is True",
        ),
        OutputAttribute(
            name="on_False",
            description="input_data when condition is False",
        )
    ]

    @classmethod
    def to_workflow_node(cls) -> WorkflowNode:
        """ Converts the node class to a plugin description dictionary.
        """
        wkf_node = super().to_workflow_node()
        wkf_node.is_branch = True
        return wkf_node

    def execute(
            self,
            input_data: Any,
            condition: Union[bool, str, None] = None,
            _engine: Optional[engine.ActionEngine] = None,
            _backend_directory: Optional[str] = None,
            _main_flow_id: Optional[str] = None,
    ) -> Tuple[Any, Any]:
        if _utils.evaluate_condition(condition, input_data):
            result = input_data, None
            ignored_output = list(self.provides)[1]
        else:
            result = None, input_data
            ignored_output = list(self.provides)[0]

        # Branch nodes in current engine/execution
        if _engine:
            flow = _engine._flow
            atom_names = _get_flow_atom_names_from_output(
                ignored_output,
                flow,
            )
            _utils.ignore_pending_atoms_in_engine(
                _engine,
                atom_names=atom_names,
            )

        # Branch nodes in backend if provided
        if _backend_directory and _main_flow_id:
            atom_names = _get_dependent_atom_names_from_backend(
                _backend_directory,
                _main_flow_id,
                ignored_output,
            )
            _utils.ignore_pending_atoms_in_backend(
                _backend_directory,
                _main_flow_id,
                atom_names=atom_names,
            )

        return result


def _get_flow_atom_names_from_output(
    output_name: str,
    flow_content: Union[flow.Flow, Dict[str, Any]],
) -> List[str]:
    """ BFS returning atom names that require the given output.
    """
    visited = set()
    queue = [output_name]

    while queue:
        name = queue.pop(0)
        for atom in flow_content:
            atom_name = (
                atom.name
                if isinstance(flow_content, flow.Flow)
                else atom
            )
            if atom_name in visited:
                continue

            atom_requires = (
                atom.requires
                if isinstance(flow_content, flow.Flow)
                else flow_content[atom_name].get("requires", [])
            )
            atom_provides = (
                atom.provides
                if isinstance(flow_content, flow.Flow)
                else flow_content[atom_name].get("provides", [])
            )
            if name in atom_requires:
                visited.add(atom_name)
                queue.extend(atom_provides)

    return list(visited)


def _get_dependent_atom_names_from_backend(
    backend_directory: str,
    main_flow_id: str,
    output_name: str,
) -> list[str]:
    """ BFS returning all atoms that require the given output from backend.
    """
    backend, _ = dir_backend.get_backend(
        temp_dir=backend_directory,
        validate=True
    )

    with contextlib.closing(backend.get_connection()) as conn:
        logbook = conn.get_logbook(dir_backend.LOGBOOK_NAME)
        flow_details = logbook.find(main_flow_id)

        # build graph from requires and provides.
        atoms = {}  # {name: {requires: [], provides: []}}
        for ad in conn.get_atoms_for_flow(flow_details.uuid):
            meta = ad.meta or {}
            atoms[ad.name] = {
                "requires": meta.get("requires", []),
                "provides": meta.get("provides", []),
            }

    # BFS from output_name
    return _get_flow_atom_names_from_output(
        output_name,
        atoms
    )
