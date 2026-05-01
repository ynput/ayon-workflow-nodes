"""
This should be as simple as possible to avoid import errors.
"""
import enum
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
from ayon_workflow.plugins.workflow.io import VideoCodecs
from ayon_workflow.plugins.workflow.sub_graphs import ExecutionMode
from ayon_workflow.plugins.workflow.usd import TurntableRenderer

__version__ = "0.0.1"


def get_plugins():
    from . import python_scripts

    class _TestEnum(enum.Enum):
        R = "RED"
        G = "GREEN"
        B = "BLUE"

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
                    "type": Union[MediaType, List[MediaType]],
                    "allow_multi_connection": True,
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
                    "name": "read_node_names",
                    "description": "Explicit a Read node to use.",
                    "type": List[str],
                    "default": [],
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
                {
                    "name": "comment",
                    "description": "The publish comment.",
                    "type": str,
                    "default": "",
                    "widget": {"name": "text"},
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
            "name": "RunPythonUV",
            "description": (
                "Run a Python snippet in an isolated uv-managed environment. "
                "Packages listed in 'requirements' are installed on demand "
                "via 'uv run --with'. Connect upstream nodes to 'inputs' to "
                "make them available as the 'inputs' list inside the script."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "snippet",
                    "description": "Python snippet to execute.",
                    "type": str,
                    "default": python_scripts.DEFAULT_SCRIPT,
                    "widget": {
                        "name": "python_code",
                        "language": "python",
                        "default_height": 440,
                    },
                },
                {
                    "name": "inputs",
                    "description": (
                        "Data from upstream nodes, available as the 'inputs' "
                        "list inside the snippet. Connect multiple upstream "
                        "nodes to pass several values."
                    ),
                    "type": Any,
                    "allow_multi_connection": True,
                },
                {
                    "name": "requirements",
                    "description": (
                        "PEP 508 package requirements "
                        "(for example 'requests>=2.28' or 'pillow')."
                    ),
                    "type": List[str],
                    "default": [],
                },
                {
                    "name": "python_version",
                    "description": (
                        "Python version for uv, for example '3.11'. "
                        "Leave empty to use the default."
                    ),
                    "type": str,
                    "default": "",
                },
            ],
            "outputs": [
                {
                    "name": "outputs",
                    "type": Any,
                }
            ],
        },
        {
            "name": "RunPythonAYON",
            "description": (
                "Run a Python snippet using AYON's Python interpreter. "
                "Connect upstream nodes to 'inputs' to make them available "
                "as the 'inputs' list inside the script."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "snippet",
                    "description": "Python snippet to execute.",
                    "type": str,
                    "default": python_scripts.DEFAULT_SCRIPT,
                    "widget": {
                        "name": "python_code",
                        "language": "python",
                        "default_height": 440,
                    },
                },
                {
                    "name": "inputs",
                    "description": (
                        "Data from upstream nodes, available as the 'inputs' "
                        "list inside the snippet. Connect multiple upstream "
                        "nodes to pass several values."
                    ),
                    "type": Any,
                    "allow_multi_connection": True,
                },
            ],
            "outputs": [
                {
                    "name": "outputs",
                    "type": Any,
                }
            ],
        },
        {
            "name": "ProductVersionRepresentation",
            "description": "Fetch a representation from a product version.",
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The product context.",
                    "type": ContextItem,
                },
                {
                    "name": "product_id",
                    "description": "The product ID",
                    "type": str,
                },
                {
                    "name": "product_version_id",
                    "description": "The product version ID",
                    "type": str,
                },
                {
                    "name": "representation_name",
                    "description": "The representation name",
                    "type": str,
                },
            ],
            "outputs": [
                {
                    "name": "output_path",
                    # TODO: allow to return a RepresentationItem ?
                    "type": Union[str, Video, Image, ImageSequence],
                }
            ],
        },
        {
            "name": "Representation",
            "description": "Prepare a representation for publishing.",
            "version": __version__,
            "inputs": [
                {
                    "name": "input_media",
                    "description": "The content to be published.",
                    "type": Union[str, MediaType],
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a content",
                        "filter": "All Files (*.*)",
                    },
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
                    "default": ExecutionMode.SERIAL.value,
                    "widget": {
                        "name": "choice",
                        "options": ExecutionMode,
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
                    "default": TextToImageModel.FLUX_SCHNELL.value,
                    "widget": {
                        "name": "choice",
                        "options": TextToImageModel,
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
                    "widget": {
                        "name": "filepath",
                        "caption": "Select an image",
                        "filter": "Image Files (*.png;*.jpg;*.jpeg)",
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
                    "default": TextTo3DModel.TRELLIS.value,
                    "widget": {
                        "name": "choice",
                        "options": TextTo3DModel,
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
                    "widget": {
                        "name": "filepath",
                        "caption": "Select the executable file",
                    },
                },
                {
                    "name": "usd_input",
                    "description": (
                        "The path to the USD asset to generate the turntable."
                    ),
                    "type": str,
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a USD scene file",
                        "filter": "USD Scene (*.usd*)",
                    },
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
                    "default": TurntableRenderer.BLENDER.value,
                    "widget": {
                        "name": "choice",
                        "options": TurntableRenderer,
                    }
                },
            ],
            "outputs": [
                {
                    "name": "output_sequence",
                    "type": ImageSequence,
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
        {
            "name": "ReviewableUpload",
            "description": (
                "Upload a reviewable representation to a product version."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The product context.",
                    "type": ContextItem,
                },
                {
                    "name": "product_version_id",
                    "description": "The product version ID",
                    "type": str,
                },
                {
                    "name": "reviewable_media",
                    "description": "The media to upload",
                    "type": Union[str, MediaType],
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a media file",
                        "filter": "All Files (*.*)",
                    },
                }
            ],
            "outputs": [],
        },
        {
            "name": "Encode",
            "description": (
                "Encode a media file to a Video."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The product context.",
                    "type": ContextItem,
                },
                {
                    "name": "input_media",
                    "description": "The input media to encode.",
                    "type": Union[str, MediaType],
                    "widget": {
                        "name": "filepath",
                        "caption": "Select a media file",
                        "filter": "All Files (*.*)",
                    },
                },
                {
                    "name": "output_media",
                    "description": "The output media to generate.",
                    "type": Union[str, Video],
                    "widget": {
                        "name": "filepath",
                        "caption": "Select an output file",
                        "filter": "Video Files (*.mp4;*.mov;*.avi)",
                    },
                },
                {
                    "name": "codec",
                    "description": "The video codec.",
                    "type": str,
                    "default": VideoCodecs.H264.value,
                    "widget": {
                        "name": "choice",
                        "options": VideoCodecs,
                    }
                },
                {
                    "name": "fps",
                    "description": "The frame rate.",
                    "type": float,
                    "default": 24.0,
                },
                {
                    "name": "slate",
                    "description": "An optional slate image.",
                    "type": Optional[Image],
                    "widget": {
                        "name": "filepath",
                        "caption": "Select an image",
                        "filter": "Image Files (*.png;*.jpg;*.jpeg)",
                    },
                }
            ],
            "outputs": [
                {
                    "name": "output_video",
                    "type": Video,
                }
            ]
        },
        {
            "name": "AppendVersionToList",
            "description": (
                "Encode a version item to an AYON server list."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The product context.",
                    "type": ContextItem,
                },
                {
                    "name": "input_versions",
                    "description": "The input version(s) to append.",
                    "type": Union[VersionItem, List[VersionItem]],
                    "allow_multiple": True,
                },
                {
                    "name": "list_label",
                    "description": "The name of the AYON list.",
                    "type": str,
                    "default": "new_AYON_list",
                },
                {
                    "name": "create_list",
                    "description": "Create the AYON list if needed.",
                    "type": bool,
                    "default": True,
                }
            ],
            "outputs": []
        },
        {
            "name": "Slater",
            "description": (
                "Generate a slate using ayon-slater."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The product context.",
                    "type": ContextItem,
                },
                {
                    "name": "input_sequence",
                    "description": "The input sequence.",
                    "type": ImageSequence,
                },
                {
                    "name": "product_base_type",
                    "description": "Product base type.",
                    "type": str,
                },
                {
                    "name": "product_name",
                    "description": "Product name.",
                    "type": str,
                },
                {
                    "name": "comment",
                    "description": "The slate comment",
                    "widget": {"name": "text"},
                    "type": str,
                    "default": "Enter slate comment here.",
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
                }
            ],
            "outputs": [
                {
                    "name": "output_slate",
                    "type": Image,
                }
            ]
        },

        ##########################    MOCKUPS    ############################
        {
            "name": "OnStatusChanged",
            "description": (
                "React from an event."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "entity_type",
                    "description": "The entity type.",
                    "type": str,
                    "widget": {
                        "name": "choice",
                        "options": ["Folder", "Version", "Task"],
                    },
                    "default": "Task",
                },
            ],
            "outputs": [
                {
                    "name": "context",
                    "type": ContextItem,
                },
                {
                    "name": "new_status",
                    "type": str,
                }
            ]
        },
        {
            "name": "GetParentFolder",
            "description": (
                "React from an event."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "context",
                    "description": "The input context.",
                    "type": ContextItem,
                },
                {
                    "name": "entity_type",
                    "description": "The entity type.",
                    "type": str,
                    "widget": {
                        "name": "choice",
                        "options": [
                            "Project",
                            "Asset",
                            "Shot",
                            "Sequence",
                            "Parent"
                        ],
                    },
                    "default": "Parent",
                },
            ],
            "outputs": [
                {
                    "name": "parent_context",
                    "type": ContextItem,
                },
            ]
        },
        {
            "name": "UpdateStatus",
            "description": (
                "Set a status to an AYON entity."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "entity",
                    "description": "The input context.",
                    "type": ContextItem,
                },
                {
                    "name": "new_status",
                    "description": "The new status.",
                    "type": str,
                },
            ],
            "outputs": [
                {
                    "name": "updated_context",
                    "type": ContextItem,
                },
            ]
        },
        {
            # TODO: implement generic "If" with taskflow deciders
            # Provide common deciders for status check etc..
            "name": "If",
            "description": (
                "Condition."
            ),
            "version": __version__,
            "inputs": [
                {
                    "name": "input_data",
                    "description": "The input data.",
                    "type": Any,
                },
                {
                    "name": "expression",
                    "description": "The condition as an expression.",
                    "type": str,
                },
            ],
            "outputs": [
                {
                    "name": "true",
                    "type": Any,
                },
                {
                    "name": "false",
                    "type": Any,
                },
            ]
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
                    "default": "GET",
                },
                {
                    "name": "choice_from_enum",
                    "description": "whatever",
                    "widget": {
                        "name": "choice",
                        "options": _TestEnum,
                    },
                    "type": str,
                    "default": _TestEnum.G.value,
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
    from . import essentials, publish, python_scripts
    from . import ai, sub_graphs, usd, product, io
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
        # IO
        "Encode": io.encode,
        "Slater": io.generate_slate,
        # Processes
        "BlenderRender": blender_render.run_blender_render,
        "BlenderWorkfile": blender_workfile.run_blender_workfile,
        "NukeRender": nuke.run_nuke_render,
        # Product
        "AppendVersionToList": product.append_version_to_server_list,
        "ProductVersionRepresentation": product.get_latest_product_path,
        "ReviewableUpload": product.upload_reviewable,
        # Publish
        "Publish": publish.publish_content,
        "Representation": publish.prepare_representation,
        "RunPythonAYON": python_scripts.run_python_ayon,
        "RunPythonUV": python_scripts.run_python_uv,
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
