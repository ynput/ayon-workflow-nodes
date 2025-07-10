""" Essential features to be exposed as nodes.
"""

import os
from typing import Optional, Any
import tempfile

from ayon_workflow.plugins.workflow._datatypes import (
    ImageSequence,
    Video,
    Folder,
    FrameRange,
)



def pass_through(input_data: Any) -> Any:
    return input_data


def get_ayon_folder(
    project_name: str,
    folder_id: Optional[str] = str,
    folder_name: Optional[str] = str,
    folder_type: Optional[str] = str,
) -> Folder:
    # TODO gather from server (id or type/name)
    # also validate it exists, raise otherwise.
    return Folder(
        project_name=project_name
    )


def _check_parent_directory(
        parent_directory: Optional[str],
    ) -> str:
    if parent_directory and not os.path.exists(parent_directory):
        raise ValueError(
            f"Provided parent directory does not exists: {parent_directory}"
        )

    elif not parent_directory:
        parent_directory = tempfile.mkdtemp()

    return parent_directory


def prepare_image_sequence(
    head: str,
    tail: str,
    parent_dir: Optional[str] = None,
    padding: Optional[int] = 4,
    frame_range: Optional[FrameRange] = None,
) -> ImageSequence:
    parent_dir = _check_parent_directory(parent_dir)
    return ImageSequence(
        directory=parent_dir,
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
        directory=os.path.join(directory, basename),
        frame_range=frame_range,
    )
