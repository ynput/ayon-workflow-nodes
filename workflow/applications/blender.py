""" plugin.workflow.applications.blender
"""

from typing import Optional
import os

from ayon_workflow.plugins.workflow._datatypes import (
    ImageSequence,
    Folder,
    FrameRange,
)

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


def run_blender_render(
        folder: Folder,
        blender_script_path: str,
        output_media: ImageSequence,
        input_resource_path: Optional[str] = None,
        python_script_path: Optional[str] = None,
        frame_range: Optional[FrameRange] = None,
        blender_application_variant: Optional[str] = None,
    ) -> ImageSequence:
    # Construct render command line args.
    app_args = [
        "-b",
        "-P",
        _base.get_render_python_script_path(
            python_script_path=python_script_path,
            default_content=_default_py_render_logic(),
        ),
        "--",
        "--blend_file",
        blender_script_path,
    ]

    # Add process-specific args
    if output_media:
        app_args.extend(
            [
                "--output_path",
                os.path.join(
                    output_media.directory,
                    f"{output_media.head}."
                )
            ]
        )
    if frame_range:
        app_args.extend(
            [
                "--start",
                str(frame_range.first_frame),
                "--end",
                str(frame_range.last_frame),
            ]
        )
    if input_resource_path:
        app_args.extend(
            [
                "--input_path",
                input_resource_path,
            ]
        )

    print(" ".join(app_args))

    # Start application.
    _ = _base.run_application(
        "blender",
        folder,
        app_args=app_args,
        app_application_variant=blender_application_variant,
    )

    # TODO: make output_media optional and
    # identify media from resulting stdout instead.
    # assert the output_media exists
    return output_media
