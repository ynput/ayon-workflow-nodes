""" Record a workflow run, then find it in the runs of the workflow.
Needs an AYON connection through a user that can create events.
"""
import logging
import os

import ayon_api

from ayon_workflow.version import __version__
from ayon_workflow.workflow_editor import Workflow
from ayon_workflow.workflow_execution import execute_workflow, WorkflowRun
from ayon_workflow.plugin_system import register_all_plugins


# Enforce service user (regular user cannot edit events).
ayon_api.close_connection()
ayon_api.init_service(
    addon_name="workflow",
    service_name="event_processor",
    token=os.getenv("AYON_API_KEY"),
)

register_all_plugins()
logging.basicConfig(level=logging.INFO)

# Runs are listed by workflow name.
my_workflow = Workflow(name="run_demo", description="this is a demo.")
my_workflow.execution_graph.create_node("NoOp")

# The run is recorded as a "workflow.run" event: started, then finished.
with WorkflowRun(my_workflow, trigger="demo_to_remove") as run:
    execute_workflow(my_workflow)

print(f"Added run {run.status} in {run.duration} s")

# Latest runs of the workflow, newest first.
response = ayon_api.get(
    f"addons/workflow/{__version__}/runs/{my_workflow.name}",
    limit=5,
)
response.raise_for_status()

print("Existing runs:")
for workflow_run in response.data:
    print(
        "- ",
        workflow_run["createdAt"],
        workflow_run["status"],
        workflow_run["trigger"],
        workflow_run["user"],
        workflow_run["machine"],
    )
