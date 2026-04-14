""" plugin.workflow.applications.nuke
"""
import os

from typing import Optional, Union, List

from ayon_workflow.datatypes import (
    MediaType,
    ContextItem,
    ImageSequence,
    FrameRange,
)
from ayon_workflow._utils import remap_input

from . import _base


def _default_py_render_logic(
        write_node_name: Optional[str] = None
    ) -> str:
    """ https://learn.foundry.com/nuke/developers/latest/pythondevguide/command_line.html
    """
    begin = """
# Default Python script from ayon-workflow.

import nuke
import sys
import os

# Load Nuke script provided as command line argument.
in_script = nuke.scriptOpen(sys.argv[1])

# Map each Read node to each provided input path.
for idx in range(2, len(sys.argv), 2):
    if sys.argv[idx] == "--output":
        break

    read_node = nuke.toNode(sys.argv[idx])
    if read_node is None:
        raise ValueError(f"Read node '{sys.argv[idx]}' not found.")
    read_node['file'].fromUserText(sys.argv[idx + 1])

"""

    if write_node_name:
        write_node = f"write_node = nuke.toNode('{write_node_name}')"
    else:
        write_node = """
# No explicit write node provided.
try:
    write_node, = nuke.allNodes("Write")
except ValueError:
    raise ValueError("Ambiguous Write node.")
"""

    input_output_media = """
# fromUserText ensures format related
# knobs are properly refreshed
write_node['file'].fromUserText(sys.argv[-1])

# save scene
current_dir = os.path.dirname(sys.argv[-1])
output = os.path.join(current_dir, "workfile.nk")
nuke.scriptSaveAs(output, overwrite=1)
"""
    return "\n".join([
        begin,
        write_node,
        input_output_media
    ])


def run_nuke_render(
        context: ContextItem,
        nuke_script_path: str,
        input_media: Union[MediaType, List[MediaType]],
        output_media: MediaType,
        python_script_path: Optional[str] = None,
        frame_range: Optional[Union[dict, FrameRange]] = None,
        read_node_names: List[str] = [],
        write_node_name: Optional[str] = None,
        nuke_application_variant: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> MediaType:

    if isinstance(frame_range, dict):
        frame_range = FrameRange(**frame_range)

    # Construct render command line args.
    app_args = ["-x"]
    if write_node_name:
        app_args = ["-X", write_node_name]

    if not output_media:
        raise ValueError("No output media specified")

    if output_media.frame_range:
        frame_range = frame_range or output_media.frame_range
    elif input_media.frame_range:
        frame_range = frame_range or input_media.frame_range

    if frame_range:
        app_args.extend(["-F", str(frame_range.format())])

    if python_script_path:
        python_script_path = _base.check_python_script_path(
            context.project_name,
            python_script_path,
        )
        temp_dir = None
    else:
        temp_dir, python_script_path = _base.get_temp_python_script_path(
            context.project_name,
            default_content=_default_py_render_logic(
                write_node_name=write_node_name,
            ),
            suffix_name="nuke_render"
        )
    app_args.append(python_script_path)

    if nuke_script_path:
        nuke_script_path = remap_input(
            nuke_script_path,
            context.project_name,
        )
        app_args.append(nuke_script_path)

    if not isinstance(input_media, list):
        input_media = [input_media]

    if len(input_media) != len(read_node_names):
        raise ValueError(
            f"Mismatch input media: {input_media} "
            f"and read nodes: {read_node_names}."
        )

    for in_media, read_node_name in zip(input_media, read_node_names):
        in_media = remap_input(in_media, context.project_name)
        app_args.extend([read_node_name, in_media.format()])

    # TODO: make output_media optional and
    # identify media from resulting stdout instead.
    # assert the output_media exists
    remapped_output_media = remap_input(output_media, context.project_name)
    app_args.extend(["--output", remapped_output_media.format()])

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
        "nuke",
        context,
        app_args=app_args,
        app_application_variant=nuke_application_variant,
        log_file=log_file,
        temporary_directory=temp_dir,
    )

    # Ensure expected output_media exists.
    if isinstance(remapped_output_media, ImageSequence):  # img seq
        # TODO: check output_media is built with a frame range
        for path in remapped_output_media:
            if not os.path.exists(path):
                raise RuntimeError(f"Expected frame {path} does not exists.")
    else:
        if not os.path.exists(remapped_output_media.path):  # video
            raise RuntimeError(
                f"Expected video {remapped_output_media.path} does not exists."
            )

    if hasattr(output_media, "frame_range"):
        output_media.frame_range = frame_range

    return output_media
