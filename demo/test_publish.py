import os
from typing import Optional, Union

import pyblish.api
import pyblish.util

from ayon_core.pipeline import install_ayon_plugins
from ayon_core.pipeline.publish import publish_plugins_discover

from ayon_workflow.plugins.workflow import (
    FolderItem,
    Video,
    ImageSequence,
    FrameRange
)


AYON_DIRECTORY = os.path.dirname(__file__)


def publish(
    path: Union[str, Video, ImageSequence],
    folder: FolderItem,
    product_name: str,
    product_type: str = "workfile",
    variant: Optional[str] = "Main",
):
    pyblish_context = pyblish.api.Context()
    pyblish_context.data["projectName"] = folder.project_name
    pyblish_context.data["folder_path"] = folder.folder_path()
    pyblish_context.data["task_name"] = folder.task_name
    pyblish_context.data["instances_to_collect"] = [
        {
            "product_name": product_name,
            "product_type": product_type,
            "variant": variant,
            "file_groups": [path]
        }
    ]

    pyblish.api.register_host("shell")

    install_ayon_plugins()
    discover_result = publish_plugins_discover()
    publish_plugins = discover_result.plugins
    print(discover_result.get_report(only_errors=False))

    for result in pyblish.util.publish_iter(
        context=pyblish_context,
        plugins=publish_plugins,
    ):
        if result["error"]:
            raise RuntimeError(repr(result))

    return [
        instance.data.get("versionEntity")
        for instance in pyblish_context
    ]

def run_demo(project_name: str):
    seq_folder = FolderItem(
        folder_name="sq_test",
        project_name=project_name,
    )
    shot_folder = FolderItem(
        folder_name="sh_test",
        parent=seq_folder,
        project_name=project_name,
        task_name="compositing",
    )

    publish(
        os.path.join(AYON_DIRECTORY, "resources", "render_script.nk"),
        shot_folder,
        "workfile_test",
        product_type="workfile"
    )

    img_seq = ImageSequence(
        directory=os.path.join(AYON_DIRECTORY, "resources"),
        head="img.",
        tail=".jpg",
        frame_range=FrameRange(first_frame=10, last_frame=11)
    )
    publish(
        img_seq,
        shot_folder,
        "render_test",
        product_type="render"
    )
