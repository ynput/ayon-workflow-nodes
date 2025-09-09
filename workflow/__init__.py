"""
This should be as simple as possible to avoid import errors.
"""

from typing import Any, Union
from ayon_workflow.datatypes import (
    MediaType,
    ImageSequence,
    Video,
    ContextItem,
    FolderItem,
    TaskItem,
    FrameRange,
    VersionItem,
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
            "name": "Context",
            "description": "Gather a valid AYON context item.",
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
                    "name": "folder_path",
                    "description": "An optional folder path.",
                    "type": str,
                },
                {
                    "name": "task_name",
                    "description": "An optional task name.",
                    "type": str,
                },
                {
                    "name": "task_type",
                    "description": "An optional task type.",
                    "type": str,
                },
                {
                    "name": "ensure_exists",
                    "description": "Assert context existence.",
                    "type": bool,
                    "default": True,
                },
            ],
            "outputs": [
                {
                    "name": "context",
                    "type": ContextItem,
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
                    "widget": {
                        "name": "filepath",
                        "select": "file",
                        "caption": "Select a directory",
                    },
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
                    "widget": {
                        "name": "filepath",
                    },
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
                    "name": "context",
                    "description": "The render context.",
                    "type": ContextItem,
                },
                {
                    "name": "nuke_script_path",
                    "description": "The path to the Nuke script.",
                    "type": str,
                },
                {
                    "name": "input_media",
                    "description": "The input media",
                    "type": MediaType,
                },
                {
                    "name": "output_media",
                    "description": "The output media",
                    "type": MediaType,
                },
                {
                    "name": "python_script_path",
                    "description": "The path to a python script.",
                    "type": str,
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a Python file",
                        "filter": "Python Script (*.py)",
                    },
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
                },
            ],
            "outputs": [
                {
                    "name": "rendered_media",
                    "type": MediaType,
                }
            ],
        },
        {
            "name": "BlenderRender",
            "description": "Perform a render through Blender.",
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The render context.",
                    "type": ContextItem,
                },
                {
                    "name": "blender_script_path",
                    "description": "The path to the Blender script.",
                    "type": str,
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a Blender scene file",
                        "filter": "Blender Scene (*.blend)",
                    },
                },
                {
                    "name": "input_resource_path",
                    "description": "A path to an input resource",
                    "type": str,
                    "widget": {"name": "filepath"},
                },
                {
                    "name": "output_media",
                    "description": "The output media",
                    "type": MediaType,
                },
                {
                    "name": "python_script_path",
                    "description": "The path to a python script.",
                    "type": str,
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a Python file",
                        "filter": "Python Script (*.py)",
                    },
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
                },
            ],
            "outputs": [
                {
                    "name": "rendered_media",
                    "type": MediaType,
                }
            ],
        },
        {
            "name": "Publish",
            "description": "Publish file(s) or a media.",
            "version": __version__,
            "inputs": [
                {
                    "name": "input_path",
                    "description": "The content to be published.",
                    "type": Union[str, MediaType],
                },
                {
                    "name": "context",
                    "description": "The publish context",
                    "type": Union[FolderItem, TaskItem],
                },
                {
                    "name": "product_type",
                    "description": "The publish product type.",
                    "type": str,
                },
                {
                    "name": "variant",
                    "description": "The publish product variant.",
                    "type": str,
                    "default": "Main",
                },
            ],
            "outputs": [
                {
                    "name": "published_version",
                    "type": VersionItem,
                }
            ],
        },
        {
            "name": "UI Test",
            "description": "Shows all supported widgets for testing",
            "version": __version__,
            "inputs": [
                {
                    "name": "string",
                    "description": "whatever",
                    "type": str,
                    "default": "some string data",
                },
                {
                    "name": "filepath",
                    "description": "whatever",
                    "widget": {"name": "filepath"},
                    "type": str,
                    "default": "/foo/bar.txt",
                },
                {
                    "name": "text",
                    "description": "whatever",
                    "widget": {"name": "text"},
                    "type": str,
                    "default": "Enter longer text with line breaks.",
                },
                {
                    "name": "choice",
                    "description": "whatever",
                    "widget": {
                        "name": "choice",
                        "options": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    },
                    "type": str,
                    "default": "/foo/bar.txt",
                },
                {
                    "name": "bool",
                    "description": "A binary choice",
                    "type": bool,
                    "default": True,
                },
                {
                    "name": "int",
                    "description": "whatever",
                    "type": int,
                    "default": 42,
                },
                {
                    "name": "enum",
                    "description": "whatever",
                    "widget": {
                        "name": "enum",
                        "fields": ["do this", "do that", "have a break"],
                    },
                    "type": int,
                    "default": 1,
                },
                {
                    "name": "float",
                    "description": "whatever",
                    "type": float,
                    "default": 1.234567,
                },
            ],
            "outputs": [],
        },
    ]


def get_plugin_function(name):
    from . import essentials, publish
    from .applications import nuke, blender

    func_mapping = {
        # Others
        "NoOp": essentials.pass_through,
        "Publish": publish.publish_content,
        "Context": essentials.get_ayon_context,
        "Video": essentials.prepare_video,
        "ImageSequence": essentials.prepare_image_sequence,
        # Processes
        "NukeRender": nuke.run_nuke_render,
        "BlenderRender": blender.run_blender_render,
    }

    return func_mapping.get(name)


def get_plugin_revert_function(name):
    return None


__all__ = [
    "get_plugins",
    "get_plugin_function",
    "get_plugin_revert_function",
]
