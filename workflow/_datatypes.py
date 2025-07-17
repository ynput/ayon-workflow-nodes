""" Data types.
"""
import os

from typing import Optional, Union, List

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

    def __iter__(self) -> List[str]:
        if not self.frame_range:
            return

        for frame in range(
            self.frame_range.first_frame,
            self.frame_range.last_frame + 1,
        ):
            frame_str = str(frame).zfill(self.padding)
            yield os.path.join(
                self.directory,
                f"{self.head}{frame_str}{self.tail}"
            )


Media = Union[ImageSequence, Video]


@dataclass
class FolderItem:
    """ An AYON folder item container.
    """
    project_name: str
    folder_type: Optional[str] = None
    folder_name: Optional[str] = None
    parent: Optional["FolderItem"] = None
    task_name: Optional[str] = None

    def folder_path(self) -> str:
        if self.parent:
            ancestor = self.parent.folder_path()
        else:
            ancestor = ""

        if self.folder_name:
            return f"{ancestor}/{self.folder_name}"

        raise ValueError(f"Not a complete folder: {self}")
