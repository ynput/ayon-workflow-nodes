""" graph execution from backend
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


# Create a new workflow.
my_workflow = graph_editor.Workflow(
    name="backend_workflow_demo",
    description="this is a demo.",
)

# Execution graph
execution_graph = my_workflow.execution_graph
video_node = execution_graph.create_node("Video", label="custom video node")
no_op = execution_graph.create_node("NoOp")
video_node["path"] = "/path/to/a/video.mov"
video_node.connect("video", no_op, "input_data")

# Dispatch graph
dispatch_graph = graph_editor.DispatchGraph(name="Basic Dispatch")
my_workflow.dispatch_graphs.append(dispatch_graph)
dispatch_node = dispatch_graph.create_node("DeadlineThinkbox")
dispatch_node.nodes = [video_node, no_op]

# Create a new backend directory on disk and convert to job description.
backend_dir = tempfile.mkdtemp(suffix="_backend")
job_desc = job_description.to_job_description(
    my_workflow,
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
        #args[0] "addon",
        #args[1]"workflow",
        #args[2]"execute",
        #args[3] "--graph-path",
        graph_path =  args[4],
        #args[5] "--backend-dir"
        backend_dir = args[6],
        #args[7] "--flow-id"
        flow_id = args[8],
    )
    print(result)

print("DONE")
