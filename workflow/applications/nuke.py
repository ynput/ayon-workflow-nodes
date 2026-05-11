""" plugin.workflow.applications.nuke
"""
import os

from typing import Optional, Union

from ayon_workflow.datatypes import (
    MediaType,
    ContextItem,
    ImageSequence,
    FrameRange,
)
from ayon_workflow._utils import remap_input

from . import _base


def _default_py_render_logic(
        read_node_name: Optional[str] = None,
        write_node_name: Optional[str] = None,
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
"""
    if read_node_name:
        read_node = f"read_node = nuke.toNode('{read_node_name}')"
    else:
        read_node = """
# No explicit read node provided.
try:
    read_node, = nuke.allNodes("Read")
except ValueError:
    raise ValueError("Ambiguous read node.")
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
read_node['file'].fromUserText(sys.argv[2])
write_node['file'].fromUserText(sys.argv[3])

# save scene
current_dir = os.path.dirname(sys.argv[3])
output = os.path.join(current_dir, "workfile.nk")
nuke.scriptSaveAs(output, overwrite=1)
"""
    return "\n".join([
        begin,
        read_node,
        write_node,
        input_output_media
    ])


def run_nuke_render(
        context: ContextItem,
        nuke_script_path: str,
        input_media: MediaType,
        output_media: MediaType,
        python_script_path: Optional[str] = None,
        frame_range: Optional[Union[dict, FrameRange]] = None,
        read_node_name: Optional[str] = None,
        write_node_name: Optional[str] = None,
        nuke_application_variant: Optional[str] = None,
        log_file: Optional[str] = None,
        restrict_to_task: Optional[bool] = False,
    ) -> MediaType:

    if isinstance(frame_range, dict):
        frame_range = FrameRange(**frame_range)

    # Construct render command line args.
    app_args = ["-x"]
    if write_node_name:
        app_args = ["-X", write_node_name]

    if output_media.frame_range:
        frame_range = frame_range or output_media.frame_range

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
                read_node_name=read_node_name,
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
    if input_media:
        input_media = remap_input(input_media, context.project_name)
        app_args.append(input_media.format())

    # TODO: make output_media optional and
    # identify media from resulting stdout instead.
    # assert the output_media exists
    remapped_output_media = remap_input(output_media, context.project_name)
    app_args.append(remapped_output_media.format())

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
        restrict_to_task=restrict_to_task,
    )

    # Ensure expected output_media exists.
    if isinstance(remapped_output_media, ImageSequence):  # img seq
        for path in remapped_output_media:
            if not os.path.exists(path):
                raise RuntimeError(f"Expected frame {path} does not exists.")
    else:
        if not os.path.exists(remapped_output_media.path):  # video
            raise RuntimeError(
                f"Expected video {remapped_output_media.path} does not exists."
            )

    return output_media
