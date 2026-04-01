"""
This should be as simple as possible to avoid import errors.
"""
from typing import Any, Union, List, Dict, Optional
import os

from ayon_workflow.datatypes import (
    MediaType,
    Image,
    ImageSequence,
    RepresentationItem,
    Video,
    ContextItem,
    FolderItem,
    PublishInput,
    TaskItem,
    FrameRange,
    VersionItem,
)
from ayon_workflow.workflow_editor import Workflow
from ayon_workflow.plugins.workflow.ai import TextToImageModel, TextTo3DModel
from ayon_workflow.plugins.workflow.sub_graphs import ExecutionMode
from ayon_workflow.plugins.workflow.usd import TurntableRenderer

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
            "name": "Append",
            "description": "Group or Append inputs as a list.",
            "version": __version__,
            "inputs": [
                {
                    "name": "inputs",
                    "description": "Any input(s).",
                    "type": Union[Any, List[Any]],
                    "allow_multi_connection": True,
                },
            ],
            "outputs": [
                {
                    "name": "appended_data",
                    "type": List[Any],
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
                        "select": "directory",
                        "caption": "Select a directory",
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
            "name": "MergeSequence",
            "description": "Merge multiple image sequence together.",
            "version": __version__,
            "inputs": [
                {
                    "name": "image_sequences",
                    "description": "Any image sequence(s).",
                    "type": Union[ImageSequence, List[ImageSequence]],
                    "allow_multi_connection": True,
                },
            ],
            "outputs": [
                {
                    "name": "merged_sequence",
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
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a Nuke scene file",
                        "filter": "Nuke Scene (*.nk)",
                    },
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
                {
                    "name": "log_file",
                    "description": "Path to output logs.",
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
                    "type": ImageSequence,
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
                {
                    "name": "log_file",
                    "description": "Path to output logs.",
                    "type": str,
                },
            ],
            "outputs": [
                {
                    "name": "rendered_media",
                    "type": ImageSequence,
                }
            ],
        },
        {
            "name": "BlenderWorkfile",
            "description": "Assemble a workfile in Blender.",
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
                    "name": "output_workfile",
                    "description": "The output workfile",
                    "type": str,
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
                    "name": "blender_application_variant",
                    "description": "An application variant to use.",
                    "type": str,
                },
                {
                    "name": "log_file",
                    "description": "Path to output logs.",
                    "type": str,
                },
            ],
            "outputs": [
                {
                    "name": "blend_workfile",
                    "type": str,
                }
            ],
        },
        {
            "name": "Publish",
            "description": "Publish file(s) or a media.",
            "version": __version__,
            "inputs": [
                {
                    "name": "input_paths",
                    "description": "The content to be published.",
                    "type": Union[PublishInput, List[PublishInput]],
                    "allow_multi_connection": True,
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
                    "name": "username",
                    "description": "The username to use while publishing.",
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

        #####################################################################
        {
            "name": "Representation",
            "description": "Prepare a representation for publishing.",
            "version": __version__,
            "inputs": [
                {
                    "name": "input_media",
                    "description": "The content to be published.",
                    "type": Union[str, MediaType],
                },
                {
                    "name": "name",
                    "description": "The representation name",
                    "type": Optional[str],
                },
                {
                    "name": "frame_range",
                    "description": "The representation frame range.",
                    "type": Optional[FrameRange],
                },
                {
                    "name": "custom_tags",
                    "description": "The representation custom tags.",
                    "type": Optional[List[str]],
                },
                {
                    "name": "tags",
                    "description": "The representation tags.",
                    "type": Optional[List[str]],
                },
            ],
            "outputs": [
                {
                    "name": "output_representation",
                    "type": RepresentationItem,
                }
            ],
        },
        {
            "name": "Workflow",
            "description": "Run a sub-workflow.",
            "version": __version__,
            "inputs": [
                {
                    "name": "workflow",
                    "description": "The workflow to run.",
                    "type": Union[Workflow, str],
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a Workflow file",
                        "filter": "Workflow file (*.json)",
                    },
                },
                {
                    "name": "workflow_inputs",
                    "description": "The workflow inputs.",
                    "type": Dict[str, Any],
                },
                {
                    "name": "input_connection_mapping",
                    "description": "The input connection mapping.",
                    "type": Dict[str, Any],
                },
                {
                    "name": "output_connection_mapping",
                    "description": "The output connection mapping.",
                    "type": Dict[str, Any],
                },
            ],
            "outputs": [
                {
                    "name": "execution_outputs",
                    "type": Dict[str, Any],
                }
            ],
        },
        {
            "name": "WorkflowLoop",
            "description": "Loop through a sub-workflow.",
            "version": __version__,
            "inputs": [
                {
                    "name": "workflow",
                    "description": "The workflow to run.",
                    "type": Union[Workflow, str],
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a Workflow file",
                        "filter": "Workflow file (*.json)",
                    },
                },
                {
                    "name": "workflow_inputs",
                    "description": "The workflow inputs.",
                    "type": List[Dict[str, Any]],
                },
                {
                    "name": "input_connection_mapping",
                    "description": "The input connection mapping.",
                    "type": Dict[str, Any],
                },
                {
                    "name": "output_connection_mapping",
                    "description": "The output connection mapping.",
                    "type": Dict[str, Any],
                },
                {
                    "name": "execution_mode",
                    "description": "The execution mode.",
                    "type": ExecutionMode,
                    "default": ExecutionMode.SERIAL,
                    "widget": {
                        "name": "enum",
                        "fields": [
                            execution_mode.value
                            for execution_mode in ExecutionMode
                        ],
                    }
                },
            ],
            "outputs": [
                {
                    "name": "execution_outputs",
                    "type": Dict[str, Any],
                }
            ],
        },
        {
            "name": "TextToImage",
            "description": "Generate an image from a prompt using fal.ai.",
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The context",
                    "type": ContextItem,
                },
                {
                    "name": "prompt",
                    "description": "The prompt to generate an image from.",
                    "type": str,
                    "widget": {
                        "name": "text",
                    },
                },
                {
                    "name": "output_directory",
                    "description": "A directory to save the generated image.",
                    "type": str,
                    "widget": {
                        "name": "filepath",
                        "select": "directory",
                        "caption": "Select a directory",
                    },
                },
                {
                    "name": "fal_api_key",
                    "description": "The API key for fal.ai.",
                    "type": str,
                    "default": os.getenv("FAL_KEY"),
                    "widget": {
                        "name": "text",
                    },
                },
                {
                    "name": "model",
                    "description": "The model to use for generating image.",
                    "type": str,
                    "default": str(list(TextToImageModel)[0]),
                    "widget": {
                        "name": "enum",
                        "fields": [
                            str(model)
                            for model in TextToImageModel
                        ],
                    }
                },
            ],
            "outputs": [
                {
                    "name": "output_image",
                    "type": Image,
                }
            ],
        },
        {
            "name": "ImageTextTo3D",
            "description": (
                "Generate a 3D model from a prompt and or"
                "an input image using fal.ai."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The context",
                    "type": ContextItem,
                },
                {
                    "name": "prompt",
                    "description": "The prompt to generate the model from.",
                    "type": Optional[str],
                    "widget": {
                        "name": "text",
                    },
                },
                {
                    "name": "image",
                    "description": "The image to generate the model from.",
                    "type": Optional[Image],
                },
                {
                    "name": "output_directory",
                    "description": "A directory to save the generated image.",
                    "type": str,
                    "widget": {
                        "name": "filepath",
                        "select": "directory",
                        "caption": "Select a directory",
                    },
                },
                {
                    "name": "fal_api_key",
                    "description": "The API key for fal.ai.",
                    "type": str,
                    "default": os.getenv("FAL_KEY"),
                    "widget": {
                        "name": "text",
                    },
                },
                {
                    "name": "model",
                    "description": "The model to use for generating image.",
                    "type": str,
                    "default": str(list(TextTo3DModel)[0]),
                    "widget": {
                        "name": "enum",
                        "fields": [
                            str(model)
                            for model in TextTo3DModel
                        ],
                    }
                },
            ],
            "outputs": [
                {
                    "name": "mormalized_usd_mesh",
                    "type": str,
                }
            ],
        },
        {
            "name": "TurntableUSD",
            "description": (
                "Generate turntable render from a normalized USD mesh."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The context",
                    "type": ContextItem,
                },
                {
                    "name": "usd_record_path",
                    "description": "Path to the usd-record executable.",
                    "type": str,
                },
                {
                    "name": "usd_input",
                    "description": (
                        "The path to the USD asset to generate the turntable."
                    ),
                    "type": str,
                },
                {
                    "name": "output_media",
                    "description": "The output media",
                    "type": ImageSequence,
                },
                {
                    "name": "image_width",
                    "description": "The output image width resolution.",
                    "type": int,
                    "default": 1920,
                },
                {
                    "name": "renderer",
                    "description": "The renderer to produce the turn images.",
                    "type": str,
                    "default": str(list(TurntableRenderer)[0]),
                    "widget": {
                        "name": "enum",
                        "fields": [
                            str(renderer)
                            for renderer in TurntableRenderer
                        ],
                    }
                },

            ],
            "outputs": [
                {
                    "name": "output_mesh",
                    "type": str,
                }
            ],
        },
        {
            "name": "FetchAttribute",
            "description": "Fetch the attribute value of a provided folder.",
            "version": __version__,
            "inputs": [
                {
                    "name": "folder",
                    "description": "The folder to fetch the attribute from.",
                    "type": FolderItem,
                },
                {
                    "name": "attribute_name",
                    "description": "The name of the attribute to fetch.",
                    "type": str,
                },
                {
                    "name": "default_value",
                    "description": (
                        "An optional default value to return "
                        "if the attribute is not found."
                    ),
                    "type": Any,
                    "default": None
                },
            ],
            "outputs": [
                {
                    "name": "attribute_value",
                    "type": Any,
                }
            ],
        },
        ######################################################################
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
                {
                    "name": "string_array",
                    "description": "whatever",
                    "type": List[str],
                    "default": ["foo", "bar", "baz"],
                },
                {
                    "name": "float_array",
                    "description": "whatever",
                    "type": List[float],
                },
                {
                    "name": "int_array",
                    "description": "whatever",
                    "type": List[int],
                },
            ],
            "outputs": [],
        },
    ]


def get_plugin_function(name):
    from . import essentials, publish
    from . import ai, sub_graphs, usd
    from .applications import nuke, blender_render, blender_workfile

    func_mapping = {
        # AI
        "TextToImage": ai.text_to_image,
        "ImageTextTo3D": ai.text_image_to_3d_model,
        # Essentials
        "Append": essentials.append,
        "Context": essentials.get_ayon_context,
        "FetchAttribute": essentials.fetch_folder_attribute,
        "ImageSequence": essentials.prepare_image_sequence,
        "MergeSequence": essentials.merge_sequences,
        "NoOp": essentials.pass_through,
        "Video": essentials.prepare_video,
        # Processes
        "BlenderRender": blender_render.run_blender_render,
        "BlenderWorkfile": blender_workfile.run_blender_workfile,
        "NukeRender": nuke.run_nuke_render,
        # Publish
        "Publish": publish.publish_content,
        "Representation": publish.prepare_representation,
        # USD
        "TurntableUSD": usd.run_turntable_with_record,
        # Workflow
        "Workflow": sub_graphs.run_subgraph,
        "WorkflowLoop": sub_graphs.run_loop_on_subgraph,
    }

    return func_mapping.get(name)


def get_plugin_revert_function(name):
    return None


__all__ = [
    "get_plugins",
    "get_plugin_function",
    "get_plugin_revert_function",
]
