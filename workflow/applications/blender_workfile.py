""" plugin.workflow.applications.blender_workfile
"""

from typing import Optional

from ayon_workflow.datatypes import (
    ContextItem,
)
from ayon_workflow.utils import remap_input

from . import _base


def run_blender_workfile(
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
