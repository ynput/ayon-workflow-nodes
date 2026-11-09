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
AYON_SERVICE_TOKEN = "TODO"
ayon_api.close_connection()
try:
    ayon_api.init_service(
        addon_name="workflow",
        service_name="event_processor",
        token=AYON_SERVICE_TOKEN,
    )
    assert ayon_api.is_service_user()

except Exception:
    raise RuntimeError(
        "Must be run as a service user in order to register workflow runs."
        f"(Invalid service token: {AYON_SERVICE_TOKEN})"
    )

register_all_plugins()
logging.basicConfig(level=logging.INFO)

my_workflow = Workflow(name="run_demo", description="this is a demo.")
my_workflow.execution_graph.create_node("NoOp")

# The run is recorded as a "workflow.run" event: started, then finished.
# Runs are associated to a workflow id, if not provided it gets automatically
# generated on the fly.
with WorkflowRun(my_workflow, trigger="demo_to_remove") as run:
    execute_workflow(my_workflow)

print(f"Added run {run.status} in {run.duration} s, id: {run.workflow_id}")

# Run another workflow execution.
# Give the same id to the next run to stack both runs together.
with WorkflowRun(
    my_workflow, trigger="demo_to_remove", workflow_id=run.workflow_id
) as second_run:
    execute_workflow(my_workflow)

print(f"Added run {second_run.status} in {second_run.duration} s")

# Latest runs of the workflow, newest first: the two runs above.
response = ayon_api.get(
    f"addons/workflow/{__version__}/workflows/{run.workflow_id}/runs",
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
