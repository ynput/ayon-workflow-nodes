from typing import Optional

from ayon_workflow.datatypes import FrameRange, ImageSequence
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

from ._utils import check_parent_directory


class ImageSequenceNode(WorkflowTaskNode):
    """Define an image sequence path (existing or not)."""

    name = "ImageSequence"
    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="directory",
            description="The path to the parent directory.",
            widget={
                "name": "filepath",
                "select": "directory",
                "caption": "Select a directory",
            },
        ),
        InputAttribute(
            name="head",
            description="The head of the sequence e.g. `img.`."
        ),
        InputAttribute(
            name="tail",
            description="The tail of the sequence e.g. `.jpg`."
        ),
        InputAttribute(
            name="frame_range",
            description="An optional frame_range."
        ),
        InputAttribute(
            name="padding",
            description="An optional frame range padding."
        ),
    ]

    outputs = [
        OutputAttribute(
            name="image_sequence",
            description="The resolved image sequence.",
        )
    ]

    def execute(
        self,
        head: str,
        tail: str,
        directory: Optional[str] = None,
        padding: Optional[int] = 4,
        frame_range: Optional[FrameRange] = None,
    ) -> ImageSequence:
        """ Resolves the image sequence path.
        """
        directory = check_parent_directory(directory)
        return ImageSequence(
            directory=directory,
            head=head,
            tail=tail,
            padding=padding,
            frame_range=frame_range,
        )
