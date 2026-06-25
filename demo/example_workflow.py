""" Workflow execution from backend
"""
import logging
import tempfile

from ayon_workflow import workflow_editor, workflow_execution
from ayon_workflow.workflow_execution.from_backend import job_description
from ayon_workflow.plugin_system import register_all_plugins


register_all_plugins()

# Debugging logs
logging.basicConfig()
logging.getLogger("taskflow").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engine").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engines.action_engine").setLevel(logging.INFO)


# Create a new workflow.
my_workflow = workflow_editor.Workflow(
    name="backend_workflow_demo",
    description="this is a demo.",
)

# Execution graph
execution_graph = my_workflow.execution_graph
video_node = execution_graph.create_node("Video", label="custom video node")
no_op = execution_graph.create_node("NoOp")
video_node["path"] = "/path/to/a/video.mov"
video_node.connect("video", no_op, "input_data")

# Append one dispatch graph that define a basic execution split.
dispatch_graph = workflow_editor.DispatchGraph(
    name="Everything as one big task"
)
my_workflow.dispatch_graphs.append(dispatch_graph)
dispatch_node = dispatch_graph.create_node("GenericDispatchTask")
dispatch_node.node_names = [   # all execution nodes at once
    video_node.name,
    no_op.name
]

# Create a new backend directory on disk and convert to job description.
# Job description will fallback to first dispatchable graph it can find.
backend_dir = tempfile.mkdtemp(suffix="_backend")
job_desc = job_description.to_job_description(
    my_workflow,
    dispatch_graph,
    backend_dir=backend_dir
)

print("JOB DESCRIPTION IS DONE / BACKEND INITIALIZED")

# Run command lines successively to execute workflow from the backend.
# (These can be executed from any machine having access to the backend,
# not necessarily the one that create the backend initially.)
for step in job_desc.steps:
    args = step.script.args
    result = workflow_execution.execute_from_backend(
        # Get command line to run.
        #args[0] "--headless",
        #args[1] "addon",
        #args[2]"workflow",
        #args[3]"execute",
        #args[4] "--graph-path",
        graph_path =  args[5],
        #args[6] "--backend-dir"
        backend_dir = args[7],
        #args[8] "--flow-id"
        slice_flow_id = args[9],
        #args[10] "--full-flow-id"
        full_flow_id = args[11],
    )
    print(result)

print("DONE")
