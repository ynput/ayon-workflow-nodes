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
random_node = my_graph.create_node("Random Number", label="custom label")
assert random_node.name == "Random Number1"  # unique, not editable
assert random_node.display_name == "custom label"
assert random_node.inputs == tuple([])
assert random_node.outputs == ("result", "revert")

# Create new node "NoOp"
no_op = my_graph.create_node("NoOp")
assert no_op.name == "NoOp1"  # unique, not editable
assert no_op.display_name == "NoOp1"  # default to node name
assert no_op.inputs == ("input",)
assert no_op.outputs == ("untouched_input", "revert")

# Create a node "Print"
print_node = my_graph.create_node("Print")
assert print_node.name == "Print1"
assert print_node.inputs == ("input_str", "template")

# Create another node "NoOp"
no_op2 = my_graph.create_node("NoOp")
assert no_op2.name == "NoOp2"

# Create a "Concatenate String" node
concat = my_graph.create_node("Concatenate String")
concat["input_B"] = "Enforce Static Value"
no_op.connect("untouched_input", concat, "input_A")
no_op.connect("untouched_input", concat, "input_C")

# Attempt to create a node which does not exist
try:
    error_node = my_graph.create_node("Missing_Node")
except ValueError:
    pass

# Connect nodes together
random_node.connect("result", no_op, "input")
random_node.connect("result", no_op2, "input")

# Edit "static" node input
print_node["input_str"] = "this is a default text to print"

# Delete no_op2
my_graph.delete_node(no_op2)

# Check resulting graph content
assert my_graph.name == "My Graph"
assert my_graph.description == "this is a demo."
assert my_graph.get_nodes() == [random_node, no_op, print_node, concat]


# Check serialization/deserialization
file_path = tempfile.NamedTemporaryFile(dir=os.getcwd(), suffix=".json").name
my_graph.export_to_file(file_path)
yet_another_graph = graph_editor.Graph.import_from_file(file_path)
assert my_graph == yet_another_graph
print(f"Output file: {file_path}")


# Execute the graph
results = graph_execution.execute_graph(my_graph)
print(f"Graph results: {results}")

print("done")
