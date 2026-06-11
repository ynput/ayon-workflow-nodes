""" plugin.workflow.applications.blender_workfile
"""
from typing import Optional

from ayon_workflow.datatypes import ContextItem
from ayon_workflow.utils import remap_input
from ayon_workflow.plugin_system.interface import WorkflowNode

from . import _base


class BlenderWorkfile(WorkflowNode):
    """ Edit a Blender workfile from a script.
    """
    version = "0.0.1"
    inputs = {
        "context": {
            "description": "The workfile context.",
        },
        "blender_script_path": {
            "description": "The path to the Blender script.",
            "widget": {
                "name": "filepath",
                "caption": "Select a Blender scene file",
                "filter": "Blender Scene (*.blend)",
            },
        },
        "input_resource_path": {
            "description": "A path to an input resource",
            "widget": {"name": "filepath"},
        },
        "output_workfile": {
            "description": "The output workfile",
        },
        "python_script_path": {
            "description": "The path to a python script.",
            "widget": {
                "name": "filepath",
                "caption": "Select a Python file",
                "filter": "Python Script (*.py)",
            },
        },
        "blender_application_variant": {
            "description": "An application variant to use.",
        },
        "log_file": {
            "description": "Path to output logs.",
        },
        "restrict_to_task": {
            "description": "Raises if context is not a Task.",
        },
    }
    outputs = {
        "blend_workfile": {
            "description": "The output workfile",
        },
    }

    def execute(
        self,
        context: ContextItem,
        blender_script_path: str,
        output_workfile: str,
        python_script_path: str = None,
        input_resource_path: Optional[str] = None,
        blender_application_variant: Optional[str] = None,
        log_file: Optional[str] = None,
        restrict_to_task: Optional[bool] = False,
    ) -> str:
        blender_script_path = remap_input(
            blender_script_path,
            context.project_name,
        )

        output_workfile = remap_input(
            output_workfile,
            context.project_name,
        )

        python_script_path = remap_input(
            python_script_path,
            context.project_name,
        )

        app_args = [
            "-b",
            "--python-exit-code", "1",  # ensure any exception in python raises
            "-P",
            python_script_path,
            "--",
            "--blend_file",
            blender_script_path,
            "--output_workfile",
            output_workfile,
        ]

        if input_resource_path:
            input_resource_path = remap_input(
                input_resource_path,
                context.project_name,
            )
            app_args.extend(
                [
                    "--input_path",
                    input_resource_path,
                ]
            )

        if log_file:
            log_file = remap_input(
                log_file,
                context.project_name,
            )

        # Start application.
        _ = _base.run_application(
            "blender",
            context,
            app_args=app_args,
            app_application_variant=blender_application_variant,
            log_file=log_file,
            restrict_to_task=restrict_to_task,
        )

        return output_workfile
