""" Demonstrate a graph with Blender + Nuke renders then publish results.

Requirement:
* A valid AYON folder path within a project
* Nuke and Blender applications correctly setup
"""
import os
import pprint

from ayon_workflow import graph_editor
from ayon_workflow import graph_execution
from ayon_workflow.plugins.workflow import FrameRange
from ayon_workflow.plugin_system import register_plugins


AYON_WORKFLOW_DIR = os.path.dirname(os.path.abspath(__file__))
FRAME_RANGE = FrameRange(
    first_frame=1,
    last_frame=5,
)


def _build_graph(
        project_name: str,
        folder_path: str,
    ) -> graph_editor.Graph:
    # Discover all available node definitions
    register_plugins.register_plugins()
    graph = graph_editor.Graph(name="Demo")

    # Retrieve context
    context_node = graph.create_node(
        "Context",
        label="AYON project"
    )
    context_node["project_name"] = project_name
    context_node["folder_path"] = folder_path

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
    publish_blender_node["product_name"] = "renderBlender"

    # Publish nodes (Nuke)
    publish_nuke_node = graph.create_node(
        "Publish",
        label="Publish Nuke render"
    )
    publish_nuke_node["product_type"] = "render"
    publish_nuke_node["product_name"] = "renderNuke"

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
        "input_path"
    )
    video_node.connect(
        "video",
        nuke_node,
        "output_media",
    )
    nuke_node.connect(
        "rendered_media",
        publish_nuke_node,
        "input_path"
    )
    return graph


def _run_graph(graph: graph_editor.Graph):
    results = graph_execution.execute_graph(graph)
    pprint.pprint(results)


def run_demo(
        project_name: str,
        folder_path: str,
    ):
    graph = _build_graph(
        project_name,
        folder_path,
    )
    _run_graph(graph)
