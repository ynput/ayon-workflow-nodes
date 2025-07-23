""" Publish features.
"""

from typing import Optional, Union

import pyblish.api
import pyblish.util

from ayon_core.pipeline import install_ayon_plugins
from ayon_core.pipeline.publish import publish_plugins_discover

from ayon_workflow.datatypes import (
    FolderItem,
    ImageSequence,
    TaskItem,
    VersionItem,
    Video,
)

def publish_content(
        input_path: Union[str, Video, ImageSequence],
        context: Union[FolderItem, TaskItem],
        product_name: str,
        product_type: str,
        variant: Optional[str] = "Main",
    ) -> VersionItem:
    pyblish_context = pyblish.api.Context()
    pyblish_context.data["projectName"] = context.project_name
    pyblish_context.data["folderPath"] = context.folder_path()
    pyblish_context.data["ayonWorkflowInstances"] = [
        {
            "product_name": product_name,
            "product_type": product_type,
            "variant": variant,
            "file_groups": [input_path]
        }
    ]

    if isinstance(context, TaskItem):
        pyblish_context.data["taskName"] = context.task_name

    pyblish.api.register_host("shell")

    install_ayon_plugins()
    discover_result = publish_plugins_discover()
    publish_plugins = discover_result.plugins

    for result in pyblish.util.publish_iter(
        context=pyblish_context,
        plugins=publish_plugins,
    ):
        if result["error"]:
            raise RuntimeError(repr(result))

    instance = tuple(pyblish_context)[0]
    data = instance.data.get("versionEntity")
    return VersionItem(
        version_id=data.get("id"),
        product_id=data.get("productId"),
        version=data.get("version"),
    )
