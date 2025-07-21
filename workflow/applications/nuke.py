""" plugin.workflow.applications.render
"""

from typing import Optional, Union

import os
import tempfile

from ._base import (
    get_application,
    FolderItem,
    FrameRange,
    ImageSequence,
    Video,
)


Media = Union[ImageSequence, Video]


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


def _get_render_python_script_path(
        python_script_path: Optional[str] = None,
        read_node_name: Optional[str] = None,
        write_node_name: Optional[str] = None,
    ):
    if python_script_path:
        if not os.path.exists(python_script_path):
            raise ValueError(
                f"Unreachable python script {python_script_path}."
            )
        return python_script_path

    # TODO implement a temporary centralized temporary directory.
    with tempfile.NamedTemporaryFile(
        suffix=".py",
        mode="w",
        delete=False
    ) as fhandler:
        fhandler.write(
            _default_py_render_logic(
                read_node_name=read_node_name,
                write_node_name=write_node_name,
            )
        )
        fhandler.flush()
        return fhandler.name


def run_nuke_render(
        folder_item: FolderItem,
        nuke_script_path: str,
        input_media: Media,
        output_media: Media,
        python_script_path: Optional[str] = None,
        frame_range: Optional[FrameRange] = None,
        read_node_name: Optional[str] = None,
        write_node_name: Optional[str] = None,
        nuke_application_variant: Optional[str] = None,
    ) -> Media:
    # Construct render command line args.
    app_args = ["-x"]
    if write_node_name:
        app_args = ["-X", write_node_name]
    if frame_range:
        app_args.extend(["-F", str(frame_range.format())])
    app_args.append(
        _get_render_python_script_path(
            python_script_path=python_script_path,
            read_node_name=read_node_name,
            write_node_name=write_node_name,
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

    # Start Nuke application.
    app_manager, app = get_application(
        "nuke",
        application_variant=nuke_application_variant
    )
    launch_context = app_manager.create_launch_context(
        app.full_name,
        project_name=folder_item.project_name,
        app_args=app_args,
    )
    process = launch_context.launch()

    # TODO: check this, how can we interceipt errors.
    if bool(process.returncode):
        raise RuntimeError("Execution failed.")

    return output_media
