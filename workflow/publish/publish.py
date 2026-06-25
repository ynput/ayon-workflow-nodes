import os
from typing import Optional, Union, List, Dict, Any

import pyblish.api
import pyblish.util

import ayon_api

from ayon_core.pipeline import install_ayon_plugins
from ayon_core.pipeline.create import get_product_name
from ayon_core.pipeline.publish import publish_plugins_discover


from ayon_workflow.datatypes import (
    FolderItem,
    PublishInput,
    TaskItem,
    VersionItem,
)
from ayon_workflow.utils import remap_input
from ayon_workflow.plugin_system import (
    InputAttribute,
    OutputAttribute,
    WorkflowTaskNode,
)


class Publish(WorkflowTaskNode):
    """Publish file(s) or a media."""

    version = "0.0.1"
    inputs = [
        InputAttribute(
            name="input_paths",
            description="The content to be published.",
            allow_multi_connection=True,
        ),
        InputAttribute(
            name="context",
            description="The publish context",
        ),
        InputAttribute(
            name="product_type",
            description="The publish product type.",
        ),
        InputAttribute(
            name="product_base_type",
            description="The publish base product type.",
        ),
        InputAttribute(
            name="username",
            description="The username to use while publishing.",
        ),
        InputAttribute(
            name="variant",
            description="The publish product variant.",
        ),
        InputAttribute(
            name="comment",
            description="The publish comment.",
            widget={"name": "text"},
        ),
        InputAttribute(
            name="host_name",
            description="The associated host name.",
        ),
        InputAttribute(
            name="context_data",
            description="Optional context data.",
        ),
        InputAttribute(
            name="instance_data",
            description="Optional instance data.",
        ),
    ]
    outputs = [
        OutputAttribute(
            name="published_version",
            description="The published version.",
        ),
    ]

    def execute(
        self,
        input_paths: Union[PublishInput, List[PublishInput]],
        context: Union[FolderItem, TaskItem],
        product_type: str,
        product_base_type: Optional[str] = None,
        username: Optional[str] = None,
        variant: str = "Main",
        comment: str = "",
        host_name: str = "workflow",
        context_data: Optional[Dict[str, Any]] = None,
        instance_data: Optional[Dict[str, Any]] = None,
    ) -> VersionItem:
        # Make public ayon api behave as other user.
        # this works only if public ayon api is using service user
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
                f"Unable to find folder '{folder_path}' "
                f"in project '{project_name}'."
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
                    f"Unable to find task '{context.task_name}' "
                    f"in folder '{folder_path}' "
                    f"in project '{project_name}'."
                )
            if (
                context.task_type
                and task_entity["taskType"] != context.task_type
            ):
                raise RuntimeError(
                    f"Task type mismatch for {context.task_name}. "
                    f"Expected: '{context.task_type}'. "
                    f"Got: '{task_entity['taskType']}'."
                )

        product_base_type = product_base_type or product_type
        product_name = get_product_name(
            project_name=project_name,
            folder_entity=folder_entity,
            task_entity=task_entity,
            product_base_type=product_base_type,
            product_type=product_type,
            host_name=host_name,
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
                "product_base_type": product_base_type,
                "variant": variant,
                "file_groups": in_data,
                "instance_data": instance_data or {},
            }
        ]

        if comment:
            pyblish_context.data["comment"] = comment

        if isinstance(context, TaskItem):
            pyblish_context.data["taskName"] = context.task_name

        if context_data:
            pyblish_context.data.update(context_data)

        pyblish.api.register_host("workflow")

        install_ayon_plugins()
        discover_result = publish_plugins_discover()
        publish_plugins = discover_result.plugins

        for result in pyblish.util.publish_iter(
            context=pyblish_context,
            plugins=publish_plugins
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
