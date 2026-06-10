""" Demonstrate a workflow with Blender + Nuke renders then publish results.

Requirement:
* A valid AYON folder path within a project
* A task within this folder (task name="Generic", task type="Generic")
* Nuke and Blender applications correctly setup
"""
import os
import pprint

from ayon_workflow.plugins.workflow import FrameRange
from ayon_workflow.plugin_system import register_plugins
from ayon_workflow import workflow_editor, workflow_execution

AYON_WORKFLOW_DIR = os.path.dirname(os.path.abspath(__file__))
FRAME_RANGE = FrameRange(
    first_frame=1,
    last_frame=5,
)


def _build_workflow(
        project_name: str,
        folder_path: str,
    ) -> workflow_editor.Workflow:
    # Discover all available node definitions
    register_plugins.register_plugins()

    workflow = workflow_editor.Workflow(name="Demo")
    graph = workflow.execution_graph

    # Retrieve context
    context_node = graph.create_node(
        "Context",
        label="AYON project"
    )
    context_node["project_name"] = project_name
    context_node["folder_path"] = folder_path
    context_node["task_name"] = "Generic"
    context_node["task_type"] = "Generic"

    # Render path
    render_node = graph.create_node(
        "ImageSequence",
        label="Prepare img sequence"
    )
    render_node["directory"] = os.path.join(
        os.path.join(AYON_WORKFLOW_DIR, "result")
    )
    render_node["head"] = "blender_render."
    render_node["tail"] = ".jpg"
    render_node["frame_range"] = FRAME_RANGE

    # Video path
    video_node = graph.create_node(
        "Video",
        label="Prepare video"
    )
    video_node["path"] = os.path.join(
        os.path.join(
            AYON_WORKFLOW_DIR,
            "result",
            "nuke_render.mov"
        )
    )

    # Blender render
    blender_node = graph.create_node(
        "BlenderRender",
        label="Render a Blender scene"
    )
    blender_node["blender_script_path"] = os.path.join(
        AYON_WORKFLOW_DIR,
        "resources",
        "workfile.blend"
    )
    blender_node["frame_range"] = FRAME_RANGE


    # Nuke render
    nuke_node = graph.create_node(
        "NukeRender",
        label="Encode render with Nuke"
    )
    nuke_node["nuke_script_path"] = os.path.join(
        AYON_WORKFLOW_DIR,
        "resources",
        "render_script.nk"
    )
    nuke_node["frame_range"] = FRAME_RANGE

    # Publish nodes (Blender)
    publish_blender_node = graph.create_node(
        "Publish",
        label="Publish Blender render"
    )
    publish_blender_node["product_type"] = "render"
    publish_blender_node["variant"] = "Blender"

    # Publish nodes (Nuke)
    publish_nuke_node = graph.create_node(
        "Publish",
        label="Publish Nuke render"
    )
    publish_nuke_node["product_type"] = "render"
    publish_nuke_node["variant"] = "Nuke"
    publish_nuke_node["context_data"] = {
        "frameStart": FRAME_RANGE.first_frame,
        "frameEnd": FRAME_RANGE.last_frame,
    }

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
    context_node.connect(
        "context",
        publish_blender_node,
        "context"
    )
    context_node.connect(
        "context",
        publish_nuke_node,
        "context"
    )
    render_node.connect(
        "image_sequence",
        blender_node,
        "output_media",
    )
    blender_node.connect(
        "rendered_media",
        nuke_node,
        "input_media"
    )
    blender_node.connect(
        "rendered_media",
        publish_blender_node,
        "input_paths"
    )
    video_node.connect(
        "video",
        nuke_node,
        "output_media",
    )
    nuke_node.connect(
        "rendered_media",
        publish_nuke_node,
        "input_paths"
    )
    return workflow


def _run_workflow(workflow: workflow_editor.Workflow):
    results = workflow_execution.execute_in_memory(workflow)
    pprint.pprint(results)


def run_demo(
        project_name: str,
        folder_path: str,
    ):
    workflow = _build_workflow(
        project_name,
        folder_path,
    )
    _run_workflow(workflow)


if __name__ == "__main__":
    run_demo(
        "TODO",  # project name
        "TODO",  # folderPath to a folder with a Generic/Generic task
    )
