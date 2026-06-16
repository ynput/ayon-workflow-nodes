import os
from typing import Optional

from ayon_workflow.datatypes import FrameRange, Video
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from ._utils import check_parent_directory


class VideoNode(WorkflowTaskNode):
    """Define a video path (existing or not)."""

    name = "Video"
    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="path",
            description="The path to the video.",
            widget={
                "name": "filepath",
                "select": "file",
                "caption": "Select a video file.",
            },
        ),
        InputAttribute(
            name="frame_range",
            description="An optional frame_range.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="video",
            description="The video object.",
        ),
    ]

    def execute(
        self,
        path: str,
        frame_range: Optional[FrameRange] = None,
    ) -> Video:
        """ Returns a Video object.
        """
        directory = os.path.dirname(path)
        basename = os.path.basename(path)
        directory = check_parent_directory(directory)

        return Video(
            path=os.path.join(directory, basename),
            frame_range=frame_range
        )
