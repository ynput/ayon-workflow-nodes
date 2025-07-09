""" plugin.workflow.applications.render
"""
import os
from typing import Optional, Tuple
from dataclasses import dataclass, field

from ayon_applications import ApplicationManager, Application


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


@dataclass
class Folder:
    """ A folder container.
    """
    project_name: str
    folder_type: Optional[str] = None
    folder_name: Optional[str] = None
    parent: Optional["Folder"] = None


def get_application(
        application_group_name: str,
        application_variant: Optional[str] = None,
    ) -> Tuple[ApplicationManager, Application]:
    app_manager = ApplicationManager()
    try:
        app_group = app_manager.app_groups[application_group_name]
    except KeyError:
        raise ValueError(f"Unknown application group name {application_group_name}.")

    # If not provided, default to latest version available.
    if application_variant is None:
        app = app_manager.find_latest_available_variant_for_group(app_group.name)

    else:
        # Retrieve explicit version.
        try:
            app = app_group.variants[application_variant]
        except KeyError:
            raise ValueError(
                f"Unknown variant {application_variant} "
                f"for application group {application_group_name}."
            )

    return app_manager, app
