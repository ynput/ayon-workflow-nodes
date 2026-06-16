""" A worlflow with Blender + Nuke
(can be executed locally or dispatched to Deadline Thinkbox).

* Blender render an image sequence from a script
* Nuke encore the resulting image sequence from Blender as a video
* Workflow is prepared to be dispatched a 3 dependent jobs on Deadline Thinkbox
"""
import os
import subprocess
import tempfile

from ayon_workflow import workflow_editor
from ayon_workflow.plugins.workflow import FrameRange
from ayon_workflow.plugin_system import register_plugins

register_plugins()


FRAME_RANGE = FrameRange(
    first_frame=1,
    last_frame=5,
)

workflow = workflow_editor.Workflow(name="Autorender")
graph = workflow.execution_graph

# Context
context_node = graph.create_node(
    "Context",
    label="AYON folder"
)
context_node["project_name"] = "TODO"
context_node["folder_path"] = "TODO"
context_node["task_name"] = "TODO"
context_node["task_type"] = "TODO"

# Image Sequence
img_seq_node = graph.create_node(
    "ImageSequence",
    label="Blender Output sequence"
)
img_seq_node["directory"] = "TODO"
img_seq_node["head"] = "blender_render."
img_seq_node["tail"] = ".jpg"
img_seq_node["frame_range"] = FRAME_RANGE

# Video path
video_node = graph.create_node(
    "Video",
    label="Output video"
)
video_node["path"] = "TODO"

# Blender render
blender_node = graph.create_node(
    "BlenderRender",
    label="Render a Blender scene"
)
blender_node["blender_script_path"] = "TODO"
blender_node["frame_range"] = FRAME_RANGE


# Nuke render
nuke_node = graph.create_node(
    "NukeRender",
    label="Encode render with Nuke"
)
nuke_node["nuke_script_path"] = "TODO"
nuke_node["frame_range"] = FRAME_RANGE


# Connections
context_node.connect(
    "context",
    nuke_node,
    "context"
)
context_node.connect(
    "context",
    blender_node,
    "context"
)
img_seq_node.connect(
    "image_sequence",
    blender_node,
    "output_media",
)
blender_node.connect(
    "rendered_media",
    nuke_node,
    "input_media"
)
video_node.connect(
    "video",
    nuke_node,
    "output_media",
)

# Dealine dispatch graph
dispatch_graph = workflow.create_dispatch_graph(name="Deadline")

prepare_split = dispatch_graph.create_node("DeadlineThinkbox", label="Prepare")
prepare_split.job_name = "Prepare"
prepare_split.comment = "Quick to execute could be merged with Blender job."
prepare_split.node_names = [context_node.name, img_seq_node.name]

# Make Blender run in its own slice to adjust pool
blender_split = dispatch_graph.create_node("DeadlineThinkbox", label="Blender")
blender_split.job_name = "Blender render"
blender_split.priority = 88
blender_split.pool = "cg_render_pool"
blender_split.node_names = [blender_node.name]

# Make Nuke run in its own slice to adjust license.
nuke_split = dispatch_graph.create_node("DeadlineThinkbox", label="Nuke")
nuke_split.job_name = "Nuke render"
nuke_split.limit_groups = ["nuke"]
nuke_split.node_names = [nuke_node.name, video_node.name]


# Serialization
file_path = tempfile.NamedTemporaryFile(dir=os.getcwd(), suffix=".json").name
workflow.export_to_file(file_path)
print(f"Workflow file: {file_path}")


# Submit on the farm
backend_directory = "TODO"  # need a directory on common storage
subprocess.run(
    [
        os.environ["AYON_EXECUTABLE"],
        "addon",
        "workflow",
        "submit",
        "--workflow-path",
        file_path,
        "--backend-dir",
        backend_directory,
# Optional
#        "--project",
#        "my_project_name",
    ]
)
