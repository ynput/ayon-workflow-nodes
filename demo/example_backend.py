""" graph editing example
"""
import logging
import tempfile

from ayon_workflow import addon, graph_editor
from ayon_workflow.graph_execution.from_backend import job_description
from ayon_workflow.plugin_system import register_plugins


register_plugins.register_plugins()

# Debugging logs
logging.basicConfig()
logging.getLogger("taskflow").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engine").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engines.action_engine").setLevel(logging.INFO)


# Create a new graph.
my_graph = graph_editor.Graph(
    name="backend_graph",
    description="this is a demo."
)
video_node = my_graph.create_node("Video", label="custom video node")
no_op = my_graph.create_node("NoOp")
video_node["path"] = "/path/to/a/video.mov"
video_node.connect("video", no_op, "input_data")

metadata_node = my_graph.create_node("DeadlineThinkbox")
metadata_node.nodes = [video_node, no_op]

# Create a new backend on disk.
backend_dir = tempfile.mkdtemp(suffix="_backend")
job_desc = job_description.to_job_description(
    my_graph,
    backend_dir=backend_dir
)

print("JOB DESCRIPTION IS DONE / BACKEND INITIALIZED")

# Run command lines successively to execute graph from the backend.
# (These can be executed from any machine having access to the backend,
# not necessarily the one that create the backend initially.)
for step in job_desc.steps:
    args = step.script.args
    result = addon.execute_from_backend(
        # Get command line to run.
        args[4],  # graph path,
        args[6],  # backend directory
        args[8],  # flow id
    )
    print(result)

print("DONE")
