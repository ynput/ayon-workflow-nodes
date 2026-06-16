import copy
from typing import Optional, Union, List, Dict, Any

from ayon_workflow.datatypes import (
    FrameRange,
    MediaType,
    RepresentationItem,
)
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class Representation(WorkflowTaskNode):
    """Prepare a representation for publishing."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_media",
            description="The content to be published.",
            allow_multi_connection=True,
            widget={
                "name": "filepath",
                "caption": "Select a content",
                "filter": "All Files (*.*)",
            },
        ),
        InputAttribute(
            name="name",
            description="The representation name",
        ),
        InputAttribute(
            name="frame_range",
            description="The representation frame range.",
        ),
        InputAttribute(
            name="data",
            description="The raw representation dict data.",
        ),
        InputAttribute(
            name="custom_tags",
            description="The representation custom tags.",
        ),
        InputAttribute(
            name="tags",
            description="The representation tags.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="output_representation",
            description="A representation ready to be published.",
        ),
    ]

    def execute(
        self,
        input_media: Union[str, MediaType, List[Union[str, MediaType]]],
        name: Optional[str] = None,
        frame_range: Optional[FrameRange] = None,
        data: Optional[Dict[str, Any]] = None,
        custom_tags: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Union[RepresentationItem, List[RepresentationItem]]:
        """Prepare a representation for publishing.
        """
        # single entry, return it as representation.
        if not isinstance(input_media, list):
            return RepresentationItem(
                input_media=input_media,
                name=name,
                frame_range=frame_range,
                data=data,
                custom_tags=custom_tags,
                tags=tags,
            )

        # multiple entries, return a list of representations replicating
        # the same data, frame_range, custom_tags, tags for each entry.
        return [
            RepresentationItem(
                input_media=media,
                name=name,
                frame_range=frame_range,
                data=copy.deepcopy(data),
                custom_tags=copy.deepcopy(custom_tags),
                tags=copy.deepcopy(tags),
            )
            for media in input_media
        ]
