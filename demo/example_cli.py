""" graph editing example
"""
import os
import json
import logging
import tempfile

from ayon_workflow import graph_editor
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

# Create new node "NoOp"
no_op = my_graph.create_node("NoOp")

# Create a node "Print"
print_node = my_graph.create_node("Print")

# Connect nodes together
random_node.connect("result", no_op, "input")
no_op.connect("untouched_input", print_node, "input_str")

# Check serialization/deserialization
file_path = tempfile.NamedTemporaryFile(dir=os.getcwd(), suffix=".json").name
my_graph.export_to_file(file_path)
print(f"Output file: {file_path}")

# inputs
input_data = {
    f"{print_node.name}.template": ("Print random number "
    "from injected input: {input_str}")
}
with tempfile.NamedTemporaryFile(
    dir=os.getcwd(),
    suffix=".json",
    mode="w+",
    delete=False
) as input_file:
    json.dump(input_data, input_file)
    print(f"Input data file: {input_file.name}")
