""" Publish features.
"""

from typing import Optional, Union, List

import pyblish.api
import pyblish.util

from ayon_core.pipeline import install_ayon_plugins
from ayon_core.pipeline.create import get_product_name
from ayon_core.pipeline.publish import publish_plugins_discover

from ayon_workflow.datatypes import (
    FolderItem,
    ImageSequence,
    TaskItem,
    VersionItem,
    Video,
)

publish_input = Union[str, Video, ImageSequence]


def publish_content(
        input_paths: Union[publish_input, List[publish_input]],
        context: Union[FolderItem, TaskItem],
        product_type: str,
        variant: Optional[str] = "Main",
    ) -> VersionItem:
    task_name = None
    task_type = None
    if isinstance(context, TaskItem):
        task_name = context.task_name
        task_type = context.task_type

    product_name = get_product_name(
        context.project_name,
        task_name,
        task_type,
        "workflow",
        product_type,
        variant,
    )

    in_data = input_paths if isinstance(input_paths, list) else [input_paths]
    pyblish_context = pyblish.api.Context()
    pyblish_context.data["projectName"] = context.project_name
    pyblish_context.data["folderPath"] = context.folder_path()
    pyblish_context.data["ayonWorkflowInstances"] = [
        {
            "product_name": product_name,
            "product_type": product_type,
            "variant": variant,
            "file_groups": in_data
        }
    ]

    if isinstance(context, TaskItem):
        pyblish_context.data["taskName"] = context.task_name

    pyblish.api.register_host("workflow")

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
