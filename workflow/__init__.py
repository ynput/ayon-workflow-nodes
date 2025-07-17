"""
This should be as simple as possible to avoid import errors.
"""
from typing import Any
from ayon_workflow.plugins.workflow._datatypes import (
    Media,
    ImageSequence,
    Video,
    FolderItem,
    FrameRange,
)

__version__ = "0.0.1"


def get_plugins():
    return [
        {
            "name": "NoOp",
            "description": "Return input as-is (no operation).",
            "version": __version__,
            "inputs": [
                {
                    "name": "input_data",
                    "description": "An input data to be returned as-is.",
                    "type": Any,
                }
            ],
            "outputs": [
                {
                    "name": "output_data",
                    "type": Any,
                }
            ],
        },
        {
            "name": "FolderItem",
            "description": "Gather a valid AYON folder item.",
            "version": __version__,
            "inputs": [
                {
                    "name": "project_name",
                    "description": "The project name",
                    "type": str,
                },
                {
                    "name": "folder_id",
                    "description": "An optional folder ID.",
                    "type": str,
                },
                {
                    "name": "folder_name",
                    "description": "An optional folder name.",
                    "type": str,
                },
                {
                    "name": "folder_type",
                    "description": "An optional folder type.",
                    "type": str,
                },
            ],
            "outputs": [
                {
                    "name": "folder_item",
                    "type": FolderItem,
                }
            ],
        },
        {
            "name": "Video",
            "description": "Define a video path (existing or not).",
            "version": __version__,
            "inputs": [
                {
                    "name": "path",
                    "description": "The path to the video.",
                    "type": str,
                    "default": "movie.mov",
                },
                {
                    "name": "frame_range",
                    "description": "An optional frame_range.",
                    "type": FrameRange,
                },
            ],
            "outputs": [
                {
                    "name": "video",
                    "type": Video,
                }
            ],
        },
        {
            "name": "ImageSequence",
            "description": "Define an image sequence path (existing or not).",
            "version": __version__,
            "inputs": [
                {
                    "name": "directory",
                    "description": "The path to the parent directory.",
                    "type": str,
                },
                {
                    "name": "head",
                    "description": "The head of the sequence e.g. `img.`.",
                    "type": str,
                    "default": "img_seq.",
                },
                {
                    "name": "tail",
                    "description": "The tail of the sequence e.g. `.jpg`.",
                    "type": str,
                    "default": ".exr",
                },
                {
                    "name": "frame_range",
                    "description": "An optional frame_range.",
                    "type": FrameRange,
                },
                {
                    "name": "padding",
                    "description": "An optional frame range padding.",
                    "type": int,
                    "default": 4,
                },
            ],
            "outputs": [
                {
                    "name": "image_sequence",
                    "type": ImageSequence,
                }
            ],
        },
        {
            "name": "NukeRender",
            "description": "Perform a render through Nuke.",
            "version": __version__,
            "inputs": [
                {
                    "name": "folder_item",
                    "description": "The folder item associated to the Render.",
                    "type": FolderItem,
                },
                {
                    "name": "nuke_script_path",
                    "description": "The path to the Nuke script.",
                    "type": str,
                },
                {
                    "name": "input_media",
                    "description": "The input media",
                    "type": Media,
                },
                {
                    "name": "output_media",
                    "description": "The output media",
                    "type": Media,
                },
                {
                    "name": "python_script_path",
                    "description": "The path to a python script.",
                    "type": str,
                },
                {
                    "name": "frame_range",
                    "description": "Restrictive frame range.",
                    "type": FrameRange,
                },
                {
                    "name": "read_node_name",
                    "description": "Explicit a Read node to use.",
                    "type": str,
                },
                {
                    "name": "write_node_name",
                    "description": "Explicit a Write node to use.",
                    "type": str,
                },
                {
                    "name": "nuke_application_variant",
                    "description": "An application variant to use.",
                    "type": str,
                }
            ],
            "outputs": [
                {
                    "name": "rendered_media",
                    "type": Media,
                }
            ],
        },
        {
            "name": "BlenderRender",
            "description": "Perform a render through Blender.",
            "version": __version__,
            "inputs": [
                {
                    "name": "folder_item",
                    "description": "The folder item associated to the Render.",
                    "type": FolderItem,
                },
                {
                    "name": "blender_script_path",
                    "description": "The path to the Blender script.",
                    "type": str,
                },
                {
                    "name": "input_resource_path",
                    "description": "A path to an input resource",
                    "type": str,
                },
                {
                    "name": "output_media",
                    "description": "The output media",
                    "type": Media,
                },
                {
                    "name": "python_script_path",
                    "description": "The path to a python script.",
                    "type": str,
                },
                {
                    "name": "frame_range",
                    "description": "Restrictive frame range.",
                    "type": FrameRange,
                },
                {
                    "name": "blender_application_variant",
                    "description": "An application variant to use.",
                    "type": str,
                }
            ],
            "outputs": [
                {
                    "name": "rendered_media",
                    "type": Media,
                }
            ],
        },
    ]


def get_plugin_function(name):
    from . import essentials
    from .applications import nuke, blender

    func_mapping = {
        # Others
        "NoOp": essentials.pass_through,

        "FolderItem": essentials.get_ayon_folder,
        "Video": essentials.prepare_video,
        "ImageSequence": essentials.prepare_image_sequence,

        # Processes
        "NukeRender": nuke.run_nuke_render,
        "BlenderRender": blender.run_blender_render
    }

    return func_mapping.get(name)


def get_plugin_revert_function(name):
    return None


__all__ = [
    "Media",
    "ImageSequence",
    "Video",
    "FolderItem",
    "FrameRange",

    "get_plugins",
    "get_plugin_function",
    "get_plugin_revert_function",
]
