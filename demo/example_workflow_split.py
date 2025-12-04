""" Workflow with multiple dispatch graphs.
"""
import logging
import tempfile

from ayon_workflow import addon, workflow_editor
from ayon_workflow.workflow_execution.from_backend import job_description
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

# Edit random execution nodes in the execution graph.
execution_graph = my_workflow.execution_graph

video_node = execution_graph.create_node("Video", label="custom video node")
no_op = execution_graph.create_node("NoOp")
video_node["path"] = "/path/to/a/video.mov"
video_node.connect("video", no_op, "input_data")

img_seq_node = execution_graph.create_node(
    "ImageSequence",
    label="custom img node"
)
append_node = execution_graph.create_node("Append")
img_seq_node["directory"] = "/path/to/a/"
img_seq_node["head"] = "img."
img_seq_node["tail"] = ".ext"
no_op.connect("output_data", append_node, "input_1")
img_seq_node.connect("image_sequence", append_node, "input_2")

# Append multiple dispatch graphs in the workflow
# Dispatch logic 1 = 1 step with everything
dispatch_graphA = workflow_editor.DispatchGraph(
    name="One Deadline Job doing Everything"
)
my_workflow.dispatch_graphs.append(dispatch_graphA)

dispatch_taskA = dispatch_graphA.create_node(
    "DeadlineThinkbox",
    label="Split2"
)
dispatch_taskA.nodes = [append_node, img_seq_node, video_node, no_op]

# Dispatch logic 2 = split as 2 steps
# Split 1 (Video node + NoOp)
# Split 2 (ImageSequence node + Append)
dispatch_graphB = workflow_editor.DispatchGraph(
    name="One Job with 2 Deadline Steps"
)
my_workflow.dispatch_graphs.append(dispatch_graphB)

dispatch_taskB1 = dispatch_graphB.create_node(
    "DeadlineThinkbox",
    label="Split2"
)
dispatch_taskB1.nodes = [append_node, img_seq_node]

dispatch_taskB2 = dispatch_graphB.create_node(
    "DeadlineThinkbox",
    label="Split1"
)
dispatch_taskB2.nodes = [video_node, no_op]

# Create a new backend directory on disk.
backend_dir = tempfile.mkdtemp(suffix="_backend")

# Split workflow using Dispatch logic 2 (2 steps)
job_desc = job_description.to_job_description(
    my_workflow,
    backend_dir=backend_dir,
    dispatch_graph_name="One Job with 2 Deadline Steps",
)

print("JOB DESCRIPTION IS DONE / BACKEND INITIALIZED")

# Run command lines successively to execute workflow from the backend.
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
