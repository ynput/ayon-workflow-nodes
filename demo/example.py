""" graph editing example
"""
import os
import logging
import tempfile

from ayon_workflow import graph_editor
from ayon_workflow import graph_execution
from ayon_workflow.plugin_system import register_plugins


register_plugins.register_plugins()

# Debugging logs
logging.basicConfig()
logging.getLogger("taskflow").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engine").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engines.action_engine").setLevel(logging.INFO)


# Create a new graph from scratch.
my_graph = graph_editor.Graph(name="My Graph", description="this is a demo.")

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

# Check resulting graph content
assert my_graph.name == "My Graph"
assert my_graph.description == "this is a demo."
assert my_graph.get_nodes() == [random_node, no_op]


# Check serialization/deserialization
file_path = tempfile.NamedTemporaryFile(dir=os.getcwd(), suffix=".json").name
my_graph.export_to_file(file_path)
yet_another_graph = graph_editor.Graph.import_from_file(file_path)
print(f"Output file: {file_path}")

# Execute the graph
results = graph_execution.execute_graph(my_graph)
print(f"Graph results: {results}")
