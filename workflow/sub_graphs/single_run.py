from typing import Union, Dict, Any

from ayon_workflow.workflow_editor import Workflow
from ayon_workflow.workflow_execution import execute_in_memory


def run_subgraph(
    workflow: Union[Workflow, str],
    workflow_inputs: Dict[str, Any],
    input_connection_mapping: Dict[str, str],
    output_connection_mapping: Dict[str, str],
) -> Dict[str, Any]:
    if isinstance(workflow, str):
        workflow = Workflow.import_from_file(workflow)

    # Split workflow_inputs based on iterations.
    if not set(input_connection_mapping).issubset(workflow_inputs.keys()):
        raise ValueError("Invalid workflow_inputs for connection_mapping.")

    inputs_data = {
        key: workflow_inputs[input_connection_mapping[key]]
        for key in input_connection_mapping
    }
    results = execute_in_memory(
        workflow,
        inputs_data=inputs_data,
    )

    return {
        output_connection_mapping[key]: results[key]
        for key in output_connection_mapping
        if key in results
    }
