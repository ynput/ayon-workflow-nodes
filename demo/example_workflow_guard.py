""" Ensure a guard node within a workflow cancel all of the dispatched job.
"""
import tempfile

from ayon_workflow import workflow_editor, workflow_execution
from ayon_workflow.plugin_system import register_all_plugins


register_all_plugins()

workflow = workflow_editor.Workflow(name="Guard on Dispatch")
graph = workflow.execution_graph

nodes = []
for _ in range(10):
    nodes.append(graph.create_node("NoOp"))

guard_node = graph.create_node("Guard")
# force guard to stop the workflow mid-execution
guard_node["condition"] = False

nodes[0].connect("output_data", guard_node, "input_data")
guard_node.connect("result", nodes[1], "input_data")


# Dealine dispatch graph
dispatch_graph = workflow.create_dispatch_graph(name="Deadline")

dispatch_task = dispatch_graph.create_node("DeadlineThinkbox")
dispatch_task.job_name = "Pre-cancel job"
dispatch_task.node_names = [nodes[0].name]

dispatch_task = dispatch_graph.create_node("DeadlineThinkbox")
dispatch_task.job_name = "Cancel workflow execution"
dispatch_task.node_names = [guard_node.name, nodes[1].name]

dispatch_task = dispatch_graph.create_node("DeadlineThinkbox")
dispatch_task.job_name = "Parallel job"
dispatch_task.node_names = [nodes[idx].name for idx in range(2, 5)]

dispatch_task = dispatch_graph.create_node("DeadlineThinkbox")
dispatch_task.job_name = "Depending job"
for idx in range(5, 10):
    guard_node.connect("result", nodes[idx], "input_data")
    dispatch_task.node_names.append(nodes[idx].name)


# Ensure dispatch task run as empty shell cause execution of
# all jobs should be cancelled by the guard node
temp_dir = tempfile.mkdtemp()
workflow_execution.submit_workflow_to_farm(
    workflow,
    temp_dir,
)
print(f"Submitted, temporary directory: {temp_dir}")
