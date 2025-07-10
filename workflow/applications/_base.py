""" plugin.workflow.applications.render
"""
import os
from typing import Optional, Tuple, List
import tempfile
import subprocess

from ayon_applications import ApplicationManager, Application

from ayon_workflow.plugins.workflow._datatypes import Folder


def get_application(
        application_group_name: str,
        application_variant: Optional[str] = None,
    ) -> Tuple[ApplicationManager, Application]:
    app_manager = ApplicationManager()
    try:
        app_group = app_manager.app_groups[application_group_name]
    except KeyError:
        raise ValueError(
            f"Unknown application group name {application_group_name}."
        )

    # If not provided, default to latest version available.
    if application_variant is None:
        app = app_manager.find_latest_available_variant_for_group(
            app_group.name
        )

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


def get_render_python_script_path(
        python_script_path: Optional[str] = None,
        default_content: Optional[str] = None,
    ):
    if python_script_path:
        if not os.path.exists(python_script_path):
            raise ValueError(
                f"Unreachable python script {python_script_path}."
            )
        return python_script_path

    if not default_content:
        raise RuntimeError("Missing default render content.")

    # TODO implement a temporary centralized temporary directory.
    with tempfile.NamedTemporaryFile(
        suffix=".py",
        mode="w",
        delete=False
    ) as fhandler:
        fhandler.write(default_content)
        fhandler.flush()
        return fhandler.name


def run_application(
        application_group_name: str,
        folder: Folder,
        app_args: Optional[List[str]] = None,
        app_application_variant: Optional[str] = None,
    ) -> subprocess.Popen:
    # Start application.
    app_manager, app = get_application(
        application_group_name,
        application_variant=app_application_variant
    )
    app_launcher = app_manager.create_launch_context(
        app.full_name,
        project_name=folder.project_name,
        app_args=app_args or [],
    )
    process = app_launcher.launch()

    process.wait()
    # TODO: check this, how can we interceipt errors.
    if bool(process.returncode):
        raise RuntimeError("Execution failed.")

    return process
