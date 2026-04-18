""" Publish features.
"""
import os

from typing import Optional, Union, List

from ayon_workflow.datatypes import (
    FolderItem,
    PublishInput,
    TaskItem,
    VersionItem,
)
from ayon_workflow._utils import remap_input
from ayon_workflow.plugins.workflow._runtime_requirements import get_ayon_api


def publish_content(
        input_paths: Union[PublishInput, List[PublishInput]],
        context: Union[FolderItem, TaskItem],
        product_type: str,
        username: Optional[str] = None,
        variant: str = "Main",
        comment: str = "",
    ) -> VersionItem:
    import pyblish.api
    import pyblish.util
    from ayon_core.pipeline import install_ayon_plugins
    from ayon_core.pipeline.create import get_product_name
    from ayon_core.pipeline.publish import publish_plugins_discover

    ayon_api = get_ayon_api()

    # Make public ayon api behave as other user
    # - this works only if public ayon api is using service user
    username = username or os.environ.get("AYON_USERNAME")
    if username:
        # ayon-python-api does not have public api function to find
        # out if is used service user. So we need to have try-except.
        con = ayon_api.get_server_api_connection()
        try:
            con.set_default_service_username(username)
        except ValueError:
            pass

    folder_path: str = context.folder_path()
    project_name: str = context.project_name
    folder_entity = ayon_api.get_folder_by_path(
        project_name=context.project_name,
        folder_path=context.folder_path(),
    )
    if not folder_entity:
        raise RuntimeError(
            f"Unable to find folder '{folder_path}' in project"
            f" '{project_name}'."
        )

    task_entity = None
    if isinstance(context, TaskItem):
        task_entity = ayon_api.get_task_by_name(
            project_name=project_name,
            folder_id=folder_entity["id"],
            task_name=context.task_name,
        )
        if not task_entity:
            raise RuntimeError(
                f"Unable to find task '{context.task_name}'"
                f" in folder '{folder_path}'"
                f" in project '{project_name}'."
            )
        if context.task_type and task_entity["taskType"] != context.task_type:
            raise RuntimeError(
                "Task type mismatch for {context.task_name}."
                f" Expected: '{context.task_type}'."
                f" Got: '{task_entity['taskType']}'."
            )

    product_name = get_product_name(
        project_name=project_name,
        folder_entity=folder_entity,
        task_entity=task_entity,
        product_base_type=product_type,
        product_type=product_type,
        host_name="workflow",
        variant=variant,
    )

    if isinstance(input_paths, list):
        in_data = [
            remap_input(input_path, project_name)
            for input_path in input_paths
        ]
    else:
        in_data = [remap_input(input_paths, project_name)]

    pyblish_context = pyblish.api.Context()
    pyblish_context.data["hostName"] = "workflow"
    pyblish_context.data["projectName"] = project_name
    pyblish_context.data["folderPath"] = folder_path
    pyblish_context.data["ayonWorkflowInstances"] = [
        {
            "product_name": product_name,
            "product_type": product_type,
            "variant": variant,
            "file_groups": in_data
        }
    ]

    if comment:
        pyblish_context.data["comment"] = comment

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
