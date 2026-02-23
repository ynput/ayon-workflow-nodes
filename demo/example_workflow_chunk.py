""" Workflow with chunked dispatch graph.
"""
from dataclasses import asdict
import logging
import pprint
import tempfile

from ayon_workflow import workflow_editor
from ayon_workflow import datatypes

from ayon_workflow.workflow_execution.from_backend import (
    chunk_img_sequence,
    job_description,
)
from ayon_workflow.plugin_system import register_plugins


register_plugins.register_plugins()

# Debugging logs
logging.basicConfig()
logging.getLogger("taskflow").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engine").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engines.action_engine").setLevel(logging.INFO)


# Create a new workflow.
my_workflow = workflow_editor.Workflow(
    name="backend_workflow_split_demo",
    description="this is a demo.",
)
execution_graph = my_workflow.execution_graph

# Image sequence
img_seq_node = execution_graph.create_node(
    "ImageSequence",
    label="custom img node"
)
img_seq_node["directory"] = "/path/to/a/"
img_seq_node["head"] = "img."
img_seq_node["tail"] = ".ext"
img_seq_node["frame_range"] = datatypes.FrameRange(
    first_frame=1,
    last_frame=10,
)

render_node = execution_graph.create_node(
    "NukeRender",
    label="Render 1"
)
render_node2 = execution_graph.create_node(
    "NukeRender",
    label="Render 2"
)
render_node3 = execution_graph.create_node(
    "BlenderRender",
    label="Render 3"
)
render_node3["frame_range"] = datatypes.FrameRange(
    first_frame=1,
    last_frame=5,
)


append_node = execution_graph.create_node("Append")
no_op_node = execution_graph.create_node("NoOp")

# Connection
img_seq_node.connect("image_sequence", render_node, "input_media")
img_seq_node.connect("image_sequence", append_node, "inputs")
render_node.connect("rendered_media", append_node, "inputs")
render_node.connect("rendered_media", render_node2, "input_media")
render_node2.connect("rendered_media", no_op_node, "input_data")
no_op_node.connect("output_data", render_node3, "input_resource_path")

# Create a chunked dispatch graph with a single
# dispatch task containing the whole execution.
dispatch_graph = my_workflow.create_dispatch_graph(
    name="One Deadline Job doing Everything"
)
dispatch_task = dispatch_graph.create_node(
    "DeadlineThinkbox",
    label="Prepping"
)
dispatch_task1 = dispatch_graph.create_node(
    "DeadlineThinkbox",
    label="Chained Rendering"
)
dispatch_task2 = dispatch_graph.create_node(
    "DeadlineThinkbox",
    label="Appending"
)
dispatch_task3 = dispatch_graph.create_node(
    "DeadlineThinkbox",
    label="Rendering from Workfile"
)

dispatch_task1.task_chunk = workflow_editor.TaskChunkParameters(
    node_name=render_node.name,
    node_input_name="input_media",
    chunk_size=4,
)
dispatch_task3.task_chunk = workflow_editor.TaskChunkParameters(
    node_name=render_node3.name,
    node_input_name="frame_range",
    chunk_size=3,
)

dispatch_task.node_names = [img_seq_node.name]
dispatch_task1.node_names = [render_node.name, render_node2.name]
dispatch_task2.node_names = [append_node.name, no_op_node.name]
dispatch_task3.node_names = [render_node3.name]

my_workflow.validate()

chunk_img_sequence.validate_chunks(
    dispatch_graph,
    my_workflow,
)

chunk_img_sequence.prepare_workflow(
    dispatch_graph,
    my_workflow,
)

# Create a new backend directory on disk.
backend_dir = tempfile.mkdtemp(suffix="_backend")

# Split workflow using Dispatch logic.
job_desc = job_description.to_job_description(
    my_workflow,
    backend_dir=backend_dir,
)

print("JOB DESCRIPTION IS DONE / BACKEND INITIALIZED")

for step in job_desc.steps:
    pprint.pprint(asdict(step))

print("DONE")
