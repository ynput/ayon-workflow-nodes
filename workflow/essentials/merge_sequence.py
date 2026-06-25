from typing import List, Union
from ayon_workflow.datatypes import FrameRange, ImageSequence
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)

class MergeSequence(WorkflowTaskNode):
    """Merge multiple image sequence together."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="image_sequences",
            description="Any image sequence(s).",
            allow_multi_connection=True,
        )
    ]
    outputs = [
        OutputAttribute(
            name="merged_sequence",
            description="The merged image sequence.",
        )
    ]

    def execute(
        self, image_sequences: Union[ImageSequence, List[ImageSequence]]
    ) -> ImageSequence:
        """ Merge multiple image sequences together.
        """
        if not image_sequences:
            raise RuntimeError("Cannot merge: no sequence provided.")

        if isinstance(image_sequences, ImageSequence):
            return image_sequences

        ref_sequence = image_sequences.pop(0)
        for img_sequence in image_sequences:
            (ref_str, _) = ref_sequence.format().rsplit(" ", 1)
            (img_str, _) = img_sequence.format().rsplit(" ", 1)
            if ref_str != img_str:
                raise RuntimeError(
                    f"Cannot merge {img_sequence} into {ref_sequence}."
                )
            ref_fr = ref_sequence.frame_range
            img_fr = img_sequence.frame_range
            ref_sequence.frame_range = FrameRange(
                first_frame=min(ref_fr.first_frame, img_fr.first_frame),
                last_frame=max(ref_fr.last_frame, img_fr.last_frame),
                step=ref_fr.step,
            )
        return ref_sequence
