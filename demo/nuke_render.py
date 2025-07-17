""" Demonstrate a Nuke render.

Requirement:
* Nuke application correctly setup
* valid AYON project
"""
import os

from ayon_workflow.plugins.workflow.applications import _base, nuke


RESOURCE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "resources"
    ),
)


def run_nuke_render(project_name: str):
    nuke_script_path = os.path.join(RESOURCE_DIR, "render_script.nk")

    current_project = _base.Folder(project_name=project_name)
    input_media = _base.ImageSequence(
        directory=RESOURCE_DIR,
        head="img.",
        tail=".jpg",
        frame_range=_base.FrameRange(
            first_frame=10,
            last_frame=11,
        )
    )
    output_media = _base.ImageSequence(
        directory=RESOURCE_DIR,
        head="output.",
        tail=".png",
    )

    nuke.run_nuke_render(
        current_project,
        nuke_script_path,
        input_media,
        output_media,
        frame_range=_base.FrameRange(first_frame=48, last_frame=52),
    )
