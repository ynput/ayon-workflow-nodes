""" Workflow editing example
"""
import os
import logging
import subprocess
import tempfile

from ayon_core.lib import is_staging_enabled

from ayon_workflow import workflow_editor
from ayon_workflow import workflow_execution
from ayon_workflow.plugin_system import register_plugins


register_plugins()

# Debugging logs
logging.basicConfig()
logging.getLogger("taskflow").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engine").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engines.action_engine").setLevel(logging.INFO)


# Create a new graph from scratch.
my_workflow = workflow_editor.Workflow(name="My Graph", description="demo.")
my_graph = my_workflow.execution_graph

# Create new node "Random number"
random_node = my_graph.create_node("Video", label="custom label")
assert random_node.name == "Video1"  # unique, not editable
assert random_node.display_name == "custom label"
assert random_node.inputs == tuple(["path", "frame_range"])
assert random_node.outputs == ("video", "revert")

# Create new node "NoOp"
no_op = my_graph.create_node("NoOp")
assert no_op.name == "NoOp1"  # unique, not editable
assert no_op.display_name == "NoOp1"  # default to node name
assert no_op.inputs == ("input_data",)
assert no_op.outputs == ("output_data", "revert")

# Create another node "NoOp"
no_op2 = my_graph.create_node("NoOp")
assert no_op2.name == "NoOp2"

# Attempt to create a node which does not exist
try:
    error_node = my_graph.create_node("Missing_Node")
except ValueError:
    pass

# Connect nodes together
random_node.connect("video", no_op, "input_data")
random_node.connect("video", no_op2, "input_data")

# Edit "static" node input
random_node["path"] = "/path/to/a/video.ext"

# Delete no_op2
my_graph.delete_node(no_op2)

# Check resulting workflow content
assert my_workflow.name == "My Graph"
assert my_workflow.description == "demo."
assert my_graph.get_nodes() == [random_node, no_op]


# Check serialization/deserialization
file_path = tempfile.NamedTemporaryFile(dir=os.getcwd(), suffix=".json").name
my_workflow.export_to_file(file_path)
yet_another_workflow = workflow_editor.Workflow.import_from_file(file_path)
print(f"Output file: {file_path}")

# Execute the workflow
results = workflow_execution.execute_workflow(my_workflow)
print(f"Graph results: {results}")


# Execute the workflow through CLI
studio_bundle_name = os.getenv("AYON_STUDIO_BUNDLE_NAME")
project_bundle_name = os.getenv("AYON_BUNDLE_NAME")
if not studio_bundle_name:
    studio_bundle_name = project_bundle_name
if studio_bundle_name == project_bundle_name:
    project_bundle_name = None

args = [
    os.environ["AYON_EXECUTABLE"],
    "addon",
    "workflow",
    "execute",
    "--workflow-path",
    file_path,
]
args.extend(["--bundle", studio_bundle_name])
if project_bundle_name:
    args.extend(["--project-bundle", project_bundle_name])

if is_staging_enabled():
    args.extend(["--use-staging"])

subprocess.run(
    args,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    check=True,
)
print("CLI execution completed")
