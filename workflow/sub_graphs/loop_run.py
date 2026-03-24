import enum

from typing import Union, Dict, List, Any, Optional

from concurrent.futures import ThreadPoolExecutor, as_completed

from ayon_workflow.workflow_editor import Workflow
from ayon_workflow.plugins.workflow.sub_graphs import single_run


class ExecutionMode(enum.Enum):
    SERIAL = "SERIAL" # one after the other
    PARALLEL = "PARALLEL" # as much as possible, multi-threaded


class SubgraphError(RuntimeError):
    """Raised when a subgraph fails to execute."""
    pass


def _run_subgraphs_serial(
    workflow: Workflow,
    inputs_chunks: List[Dict[str, Any]],
    input_connection_mapping: Dict[str, str],
    output_connection_mapping: Dict[str, str],
) -> List[Dict[str, Any]]:
    results = []
    for inputs_chunk in inputs_chunks:

        try:
            result = single_run.run_subgraph(
                workflow,
                inputs_chunk,
                input_connection_mapping,
                output_connection_mapping,
            )
        except Exception as error:
            raise SubgraphError(
                f"Subgraph failed with error: {error}\n"
                f"Inputs: {inputs_chunk}\n"
                f"Workflow: {workflow.to_json()}"
            ) from error
        else:
            results.append(result)

    return results


def _run_subgraphs_parallel(
    workflow: Workflow,
    inputs_chunks: List[Dict[str, Any]],
    input_connection_mapping: Dict[str, str],
    output_connection_mapping: Dict[str, str],
) -> List[Optional[Dict[str, Any]]]:
    results: List[Optional[Dict[str, Any]]] = [None] * len(inputs_chunks)
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                single_run.run_subgraph,
                workflow,
                chunk,
                input_connection_mapping,
                output_connection_mapping,
            ): idx
            for idx, chunk in enumerate(inputs_chunks)
        }
        for future in as_completed(futures):
            idx = futures[future]

            try:
                results[idx] = future.result()
            except Exception as error:
                # Cancel all futures if any subgraph fails.
                for future in futures:
                    future.cancel()
                executor.shutdown(wait=False, cancel_futures=True)
                raise SubgraphError(
                    f"Subgraph {idx} failed with error: {error}\n"
                    f"Inputs: {inputs_chunks[idx]}\n"
                    f"Workflow: {workflow.to_json()}"
                ) from error

    return results


def run_loop_on_subgraph(
    workflow: Union[Workflow, str],
    workflow_inputs: Dict[str, List[Any]],
    input_connection_mapping: Dict[str, str],
    output_connection_mapping: Dict[str, str],
    execution_mode: Union[str, ExecutionMode] = ExecutionMode.SERIAL,
) -> List[Dict[str, Any]]:
    if isinstance(workflow, str):
        workflow = Workflow.import_from_file(workflow)

    if isinstance(execution_mode, str):
        execution_mode = ExecutionMode(execution_mode)

    workflow_inputs_copy = {
        key: workflow_inputs[key] for key in input_connection_mapping
    }

    # Package up inputs into chunks for succesive executions.
    n_chunks = len(next(iter(workflow_inputs_copy.values())))
    inputs_chunks = []
    for idx in range(n_chunks):
        try:
            inputs_chunks.append(
                {
                    key: workflow_inputs_copy[key][idx]
                    for key in input_connection_mapping
                }
            )
        except (KeyError, IndexError) as error:
            raise ValueError(
                "Input connection mapping do not match workflow inputs."
            ) from error

    if execution_mode == ExecutionMode.SERIAL:
        return _run_subgraphs_serial(
            workflow,
            inputs_chunks,
            input_connection_mapping,
            output_connection_mapping,
        )
    elif execution_mode == ExecutionMode.PARALLEL:
        return _run_subgraphs_parallel(
            workflow,
            inputs_chunks,
            input_connection_mapping,
            output_connection_mapping,
        )

    raise ValueError(
        f"Unsupported execution mode: {execution_mode}"
    )
