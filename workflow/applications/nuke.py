""" plugin.workflow.applications.nuke
"""

from typing import Optional

from ayon_workflow.datatypes import (
    MediaType,
    FolderItem,
    FrameRange,
    ImageSequence,
    Video,
)

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
"""
    return "\n".join([
        begin,
        read_node,
        write_node,
        input_output_media
    ])


def run_nuke_render(
        folder_item: FolderItem,
        nuke_script_path: str,
        input_media: MediaType,
        output_media: MediaType,
        python_script_path: Optional[str] = None,
        frame_range: Optional[FrameRange] = None,
        read_node_name: Optional[str] = None,
        write_node_name: Optional[str] = None,
        nuke_application_variant: Optional[str] = None,
    ) -> MediaType:
    # Construct render command line args.
    app_args = ["-x"]
    if write_node_name:
        app_args = ["-X", write_node_name]
    if frame_range:
        app_args.extend(["-F", str(frame_range.format())])
    app_args.append(
        _base.get_render_python_script_path(
            python_script_path=python_script_path,
            default_content=_default_py_render_logic(
                read_node_name=read_node_name,
                write_node_name=write_node_name,
            )
        )
    )
    if nuke_script_path:
        app_args.append(nuke_script_path)
    if input_media:
        app_args.append(input_media.format())

    # TODO: make output_media optional and
    # identify media from resulting stdout instead.
    # assert the output_media exists
    app_args.append(output_media.format())

    # Start application.
    _ = _base.run_application(
        "nuke",
        folder_item,
        app_args=app_args,
        app_application_variant=nuke_application_variant,
    )

    return output_media
