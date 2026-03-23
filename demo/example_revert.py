""" Workflow revert execution example
"""
import logging

from ayon_workflow.workflow_editor import Workflow
from ayon_workflow.workflow_execution import(
    execute_workflow,
    WorkflowExecutionError
)
from ayon_workflow.plugin_system import register_plugins


register_plugins.register_plugins()

# Debugging logs
logging.basicConfig()
logging.getLogger("taskflow").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engine").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engines.action_engine").setLevel(logging.INFO)


class MemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(self.format(record))

    def filter_lines(self, pattern: str) -> list[str]:
        """Return logs that match the pattern regex."""
        return [line for line in self.records if pattern in line]


# Create a new graph from scratch.
my_workflow = Workflow(name="My Workflow", description="this is a demo.")
my_graph = my_workflow.execution_graph

image_sequence_node = my_graph.create_node(
    "ImageSequence",
    label="custom image sequence"
)
nuke_process_node = my_graph.create_node("NukeRender")
image_sequence_node.connect(
    "image_sequence",
    nuke_process_node,
    "input_media"
)
image_sequence_node.connect(
    "image_sequence",
    nuke_process_node,
    "output_media"
)

# Create another "NoOp" node to be additionally
# executed on image_sequence_node revert
revert_node = my_graph.create_node("NoOp", label="Call on revert")
image_sequence_node.connect("revert", revert_node, "input_data")

memory_handler = MemoryLogHandler()
logger = logging.getLogger("example_revert")
logger.setLevel(logging.DEBUG)
logger.addHandler(memory_handler)

# Execute the workflow.
# NukeRender task will fail as no context was provided.
try:
    _ = execute_workflow(my_workflow, log=logger)

# With raise node, graph execution is expected to fail.
except WorkflowExecutionError as error:
    # Ensure the revert node was called on failure.
    print(error)
    assert memory_handler.filter_lines(
        "'REVERTED' from state 'REVERTING' with result '[ImageSequence"
    )
    print("NoOp SUCCESSFULLY called on revert")
