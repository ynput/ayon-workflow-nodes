""" split graph execution as multiple steps
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
# Split 1 (Video node + NoOp)
video_node = my_graph.create_node("Video", label="custom video node")
no_op = my_graph.create_node("NoOp")
video_node["path"] = "/path/to/a/video.mov"
video_node.connect("video", no_op, "input_data")


# Split 2 (ImageSequence node + Append)
img_seq_node = my_graph.create_node("ImageSequence", label="custom img node")
append_node = my_graph.create_node("Append")
img_seq_node["directory"] = "/path/to/a/"
img_seq_node["head"] = "img."
img_seq_node["tail"] = ".ext"
no_op.connect("output_data", append_node, "input_1")
img_seq_node.connect("image_sequence", append_node, "input_2")

metadata_container2 = my_graph.create_metadata_container(
    "DeadlineThinkbox",
    label="Split2"
)
metadata_container2.nodes = [append_node, img_seq_node]

metadata_container1 = my_graph.create_metadata_container(
    "DeadlineThinkbox",
    label="Split1"
)
metadata_container1.nodes = [video_node, no_op]

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
        args[10] if len(args) > 10 else None,  # main flow id if provided
    )
    print(result)

print("DONE")
