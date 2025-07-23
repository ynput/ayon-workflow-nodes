import os
from typing import Union, List

import pyblish.api

from ayon_core.pipeline import KnownPublishError


from ayon_workflow.plugins.workflow import (
    ImageSequence,
    Video,
)


class CollectFromProvidedFiles(pyblish.api.ContextPlugin):
    """ Collect instances prepared by the Publish node."""
    label = "Collect From Provided Files"
    order = pyblish.api.CollectorOrder - 0.5
    hosts = ["workflow"]

    @staticmethod
    def _get_paths(
        file_entry: Union[str, ImageSequence, Video]
    ) -> Union[str, List[str]]:
        if isinstance(file_entry, str):
            return file_entry
        if isinstance(file_entry, Video):
            return file_entry.path
        if isinstance(file_entry, ImageSequence):
            return list(file_entry)

        raise TypeError(f"Unsupported file entry provided: {file_entry}")

    def process(self, context):
        context.data["currentFile"] = os.path.join(os.getcwd(), "<workflow>")
        instances_to_collect = context.data.pop(
            "ayonWorkflowInstances",
            None
        )
        if not instances_to_collect:
            return

        mandatory_keys = {
            "product_name",
            "product_type",
            "variant",
            "file_groups",
        }
        for instance_to_collect in instances_to_collect:

            if (
                not isinstance(instance_to_collect, dict)
                or not mandatory_keys.issubset(set(instance_to_collect.keys()))
            ):
                raise KnownPublishError(
                    f"Invalid instance to be collected: {instances_to_collect}"
                    f" Missing mandatory keys: {mandatory_keys}."
                )

            instance_data = {
                "publish": True,
                "active": True,
                "label": instance_to_collect["product_name"],
                "name": instance_to_collect["product_name"],
                "productName": instance_to_collect["product_name"],
                "productType": instance_to_collect["product_type"],
                "family": instance_to_collect["product_type"],
                "families": [instance_to_collect["product_type"]],
                "folderPath": context.data["folderPath"],
                "task": context.data.get("taskName"),
                "variant": instance_to_collect["variant"],
                "representations": [],
            }
            for file_group in instance_to_collect["file_groups"]:
                paths = self._get_paths(file_group)
                path = paths[0] if isinstance(paths, list) else paths
                _, ext = os.path.splitext(path)
                ext = ext.strip(".")

                if isinstance(paths, list):
                    files = [os.path.basename(pth) for pth in paths]
                else:
                    files = os.path.basename(paths)

                repre = {
                    "name": ext,
                    "ext": ext,
                    "files": files,
                    "stagingDir": os.path.dirname(path),
                }
                instance_data["representations"].append(repre)

            instance = context.create_instance(instance_data["productName"])
            instance.data.update(instance_data)
