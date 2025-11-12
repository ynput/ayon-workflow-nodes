""" plugin.workflow.applications.render
"""
import pprint
import os
import sys
import subprocess
import tempfile

from typing import Optional, Tuple, List

from ayon_applications import ApplicationManager, Application, LaunchTypes
from ayon_core.pipeline import tempdir

from ayon_workflow.datatypes import ContextItem


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


def _clean_up_pyside_in_env_path(env: str) -> str:
    # AYON-launcher adds Pyside6 in the environment.
    # This is causing issues when starting DCC such as Nuke from subprocesses.
    paths = env.split(";")
    paths_to_remove = [
        path for path in paths
        if "PySide6" in path.split(os.sep)
    ]

    for path_to_remove in paths_to_remove:
        paths.remove(path_to_remove)

    return ";".join(paths)


def get_render_python_script_path(
        project_name: str,
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

    temp_dir = tempdir.get_temp_dir(project_name)
    with tempfile.NamedTemporaryFile(
        suffix=".py",
        mode="w",
        dir=temp_dir,
        delete=False
    ) as fhandler:
        fhandler.write(default_content)
        fhandler.flush()
        return fhandler.name


def run_application(
        application_group_name: str,
        context: ContextItem,
        app_args: Optional[List[str]] = None,
        app_application_variant: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> subprocess.Popen:
    # Start application.
    app_manager, app = get_application(
        application_group_name,
        application_variant=app_application_variant
    )

    launch_context = app_manager.create_launch_context(
        app.full_name,
        project_name=context.project_name,
        app_args=app_args or [],
        launch_type=LaunchTypes.automated,
    )

    log_file = log_file or os.devnull

    launch_args = launch_context.launch_args
    kwargs = launch_context.kwargs
    kwargs.update({
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
    })
    env = kwargs.get("env", {})
    env["PATH"] = _clean_up_pyside_in_env_path(
        env.get("PATH", "")
    )

    with open(log_file, "w") as f:
        f.write(f"command line: {launch_args}\n")
        f.write(f"environment: {pprint.pformat(env)}\n")
        process = subprocess.Popen(launch_args, **kwargs)

        for cha_ in iter(lambda: process.stdout.read(1), b""):
            sys.stdout.write(cha_)
            f.write(cha_)

            if process.poll() is not None and cha_ == '':
                break

        process.wait()

        # TODO: check this, how can we interceipt errors.
        if bool(process.returncode):
            f.write(f"Process failed with returncode: {process.returncode}\n")
            cmd_line = " ".join(launch_context.launch_args)
            raise RuntimeError(
                f"Command line failed: {cmd_line} "
                f"with return code: {process.returncode}"
            )

    return process
