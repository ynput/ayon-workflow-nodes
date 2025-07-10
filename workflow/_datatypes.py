""" Data types.
"""
import os

from typing import Optional, Union

from dataclasses import dataclass


@dataclass
class FrameRange:
    """ A frame range container.
    """
    first_frame: int
    last_frame: int
    step: int = 1

    # TODO: implement missing frames

    def format(self) -> str:
        if self.step == 1:
            return f"{self.first_frame}-{self.last_frame}"

        return f"{self.first_frame}-{self.last_frame}x{self.step}"


@dataclass
class Video:
    """ A media container.
    """
    path: str
    frame_range: Optional[FrameRange] = None

    def format(self) -> str:
        return self.path


@dataclass
class ImageSequence:
    """ An image sequence container.
    """
    directory: str
    head: str
    tail: str
    padding: int = 4
    frame_range: Optional[FrameRange] = None

    def format(self) -> str:
        seq = os.path.join(
            self.directory,
            f"{self.head}%0{self.padding}d{self.tail}"
        )
        if self.frame_range:
            return f"{seq} {self.frame_range.format()}"

        return seq


Media = Union[ImageSequence, Video]


@dataclass
class Folder:
    """ A folder container.
    """
    project_name: str
    folder_type: Optional[str] = None
    folder_name: Optional[str] = None
    parent: Optional["Folder"] = None

