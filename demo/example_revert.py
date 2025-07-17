""" revert graph execution example
"""
import logging

from ayon_workflow.graph_editor import graph
from ayon_workflow.graph_execution import to_taskflow
from ayon_workflow.plugin_system import register_plugins


register_plugins.register_plugins()

# Debugging logs
logging.basicConfig()
logging.getLogger("taskflow").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engine").setLevel(logging.DEBUG)
logging.getLogger("taskflow.engines.action_engine").setLevel(logging.INFO)


# Create a new graph from scratch.
my_graph = graph.Graph(name="My Graph", description="this is a demo.")

# Create new "Random number" and "Write to File"
random_node = my_graph.create_node("Random Number", label="custom label")
write_node = my_graph.create_node("Write to File")

# Write random number to a file
random_node.connect("result", write_node, "content")

# Add ensure graph fail with an additiona "Fail" node
fail_node = my_graph.create_node("Fail")

# Write random number to a file
random_node.connect("result", write_node, "content")

# Connect file path to fail message
# (This way we ensure it happens after file is created)
write_node.connect("filepath", fail_node, "message")


# Create a node "Print" to be additionally executed on write_node revert
print_node = my_graph.create_node("Print")
print_node["template"] = "Deleting file: {input_str}."
write_node.connect("revert", print_node, "input_str")

# Execute the graph
try:
    _ = to_taskflow.execute_graph(my_graph)

# With raise node, graph execution is expected to fail.
except to_taskflow.GraphExecutionError as error:
    print(error)
