""" Essential features to be exposed as nodes.
"""

import os
from typing import Optional, Any
import tempfile

from ayon_workflow.plugins.workflow._datatypes import (
    ImageSequence,
    Video,
    FolderItem,
    FrameRange,
)



def pass_through(input_data: Any) -> Any:
    return input_data


def get_ayon_folder(
    project_name: str,
    folder_id: Optional[str] = str,
    folder_name: Optional[str] = str,
    folder_type: Optional[str] = str,
) -> FolderItem:
    # TODO gather from server (id or type/name)
    # also validate it exists, raise otherwise.
    return FolderItem(
        project_name=project_name
    )


def _check_parent_directory(
        parent_directory: Optional[str],
    ) -> str:
    if parent_directory:
        os.makedirs(parent_directory, exist_ok=True)

    elif not parent_directory:
        parent_directory = tempfile.mkdtemp()

    return parent_directory


def prepare_image_sequence(
    head: str,
    tail: str,
    directory: Optional[str] = None,
    padding: Optional[int] = 4,
    frame_range: Optional[FrameRange] = None,
) -> ImageSequence:
    directory = _check_parent_directory(directory)
    return ImageSequence(
        directory=directory,
        head=head,
        tail=tail,
        padding=padding,
        frame_range=frame_range,
    )


def prepare_video(
    path: str,
    frame_range: Optional[FrameRange] = None,
) -> Video:
    directory = os.path.dirname(path)
    basename = os.path.basename(path)

    directory = _check_parent_directory(directory)
    return Video(
        path=os.path.join(directory, basename),
        frame_range=frame_range,
    )
