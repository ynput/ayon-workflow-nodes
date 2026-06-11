""" plugin.workflow.applications.blender_render
"""

from typing import Optional, Union
import os

from ayon_workflow.datatypes import (
    ImageSequence,
    ContextItem,
    FrameRange,
)

from ayon_workflow.utils import remap_input
from ayon_workflow.plugin_system.interface import WorkflowNode

from . import _base


def _default_py_render_logic() -> str:
    return """
# Default Python script from ayon-workflow.
import bpy
import sys
import argparse
import os

argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
else:
    argv = []

parser = argparse.ArgumentParser()
parser.add_argument(
    "--blend_file",
    type=str,
    required=True,
)
parser.add_argument(
    "--start",
    type=int,
)
parser.add_argument(
    "--end",
    type=int,
)
parser.add_argument(
    "--output_path",
    type=str,
    required=True,
)
parser.add_argument(
    "--input_path",
    type=str,
)
args = parser.parse_args(argv)

bpy.ops.wm.open_mainfile(filepath=args.blend_file)

scene = bpy.context.scene
scene.frame_start = args.start
scene.frame_end = args.end
scene.render.filepath = args.output_path
scene.render.use_file_extension = True
scene.render.use_overwrite = True

if args.start and args.end:
    scene.frame_start = args.start
    scene.frame_end = args.end

if args.input_path:
    ext = os.path.splitext(args.input_path)[1].lower()

    if ext == ".vdb":
        bpy.ops.object.volume_import(filepath=args.input_path)

    elif ext == ".abc":
        bpy.ops.wm.alembic_import(filepath=args.input_path)

    else:
        print(f"Unsupported input extension : {ext}")

bpy.ops.render.render(animation=True)
"""


class BlenderRender(WorkflowNode):
    """ Renders a Blender scene using a given script and input resource.
    """
    version = "0.0.1"
    inputs = {
        "context": {
            "description": "The render context.",
        },
        "blender_script_path": {
            "description": "The path to the Blender script.",
            "widget": {
                "name": "filepath",
                "caption": "Select a Blender scene file",
                "filter": "Blender Scene (*.blend)",
            },
        },
        "input_resource_path": {
            "description": "A path to an input resource",
            "widget": {"name": "filepath"},
        },
        "output_media": {
            "description": "The output media",
        },
        "python_script_path": {
            "description": "The path to a python script.",
            "widget": {
                "name": "filepath",
                "caption": "Select a Python file",
                "filter": "Python Script (*.py)",
            },
        },
        "frame_range": {
            "description": "Restrictive frame range.",
        },
        "blender_application_variant": {
            "description": "An application variant to use.",
        },
        "log_file": {
            "description": "Path to output logs.",
        },
        "restrict_to_task": {
            "description": "Raises if context is not a Task.",
        },
    }
    outputs = {
        "rendered_media": {
            "description": "The rendered media output.",
        },
    }

    def execute(
        self,
        context: ContextItem,
        blender_script_path: str,
        output_media: ImageSequence,
        input_resource_path: Optional[str] = None,
        python_script_path: Optional[str] = None,
        frame_range: Optional[Union[dict, FrameRange]] = None,
        blender_application_variant: Optional[str] = None,
        log_file: Optional[str] = None,
        restrict_to_task: Optional[bool] = False,
    ) -> ImageSequence:
        # Construct render command line args.
        blender_script_path = remap_input(
            blender_script_path,
            context.project_name,
        )

        if python_script_path:
            python_script_path = _base.check_python_script_path(
                context.project_name,
                python_script_path,
            )
            temp_dir = None

        else:
            temp_dir, python_script_path = _base.get_temp_python_script_path(
                context.project_name,
                default_content=_default_py_render_logic(),
                suffix_name="blender_render"
            )

        app_args = [
            "-b",
            "--python-exit-code", "1",  # ensure any exception in python raises
            "-P", python_script_path,
            "--",
            "--blend_file",
            blender_script_path,
        ]

        # Add process-specific args
        if output_media.frame_range:
            frame_range = frame_range or output_media.frame_range

        if frame_range:
            if isinstance(frame_range, dict):
                frame_range = FrameRange(**frame_range)
            output_media.frame_range = frame_range

            app_args.extend(
                [
                    "--start",
                    str(frame_range.first_frame),
                    "--end",
                    str(frame_range.last_frame),
                ]
            )

        remapped_output_media = remap_input(output_media, context.project_name)
        app_args.extend(
            [
                "--output_path",
                os.path.join(
                    remapped_output_media.directory,
                    f"{remapped_output_media.head}"
                )
            ]
        )

        if input_resource_path:
            input_resource_path = remap_input(
                input_resource_path,
                context.project_name,
            )
            app_args.extend(
                [
                    "--input_path",
                    input_resource_path,
                ]
            )

        if log_file:
            # Ensure logfile is unique per frame chunk.
            if frame_range:
                log_file = (
                    f"{log_file}._chunk{frame_range.first_frame}"
                    f"_{frame_range.last_frame}"
                )

            log_file = remap_input(
                log_file,
                context.project_name,
            )

        # Start application.
        _ = _base.run_application(
            "blender",
            context,
            app_args=app_args,
            app_application_variant=blender_application_variant,
            log_file=log_file,
            temporary_directory=temp_dir,
            restrict_to_task=restrict_to_task,
        )

        # Ensure expected output_media exists.
        for path in remapped_output_media:
            if not os.path.exists(path):
                raise RuntimeError(f"Expected frame {path} does not exists.")

        # TODO: make output_media optional and
        # identify media from resulting stdout instead.
        return output_media
