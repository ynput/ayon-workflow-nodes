""" plugin.workflow.applications.render
"""
import json
import os
import shutil
import sys
import subprocess
import tempfile

from contextlib import contextmanager
from typing import Optional, Tuple, List, Dict

from ayon_applications import ApplicationManager, Application, LaunchTypes
from ayon_core.pipeline import tempdir

from ayon_workflow.datatypes import ContextItem, TaskItem
from ayon_workflow._utils import remap_input


@contextmanager
def force_stdout_utf8():
    original_encoding = sys.stdout.encoding
    original_errors = sys.stdout.errors

    try:
        sys.stdout.reconfigure(encoding='utf-8')
        yield

    finally:
        sys.stdout.reconfigure(
            encoding=original_encoding,
            errors=original_errors
        )


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
        if app is None:
            raise RuntimeError(
                "Cannot find valid application with reachable executable "
                f"for application group: {app_group.name}."
            )

    else:
        # Retrieve explicit version.
        try:
            app = app_group.variants[application_variant]
        except KeyError:
            raise RuntimeError(
                f"Unknown variant {application_variant} "
                f"for application group {application_group_name}."
            )

    return app_manager, app


def check_python_script_path(
        project_name: str,
        python_script_path: Optional[str] = None,
    ) -> str:
    """ Ensure the provided python script path exists.
    """
    remap_script_path = remap_input(
        python_script_path,
        project_name,
    )

    if not os.path.exists(remap_script_path):
        raise ValueError(
            f"Unreachable python script {remap_script_path}."
        )

    return remap_script_path


def get_temp_python_script_path(
        project_name: str,
        default_content: str,
        suffix_name: str = "",
    ) -> Tuple[str]:
    """ Create a temporary python script path from content.
    """
    if not default_content:
        raise RuntimeError("Missing default render content.")

    suffix_name = f"_workflow_{suffix_name}"
    temp_dir = tempdir.get_temp_dir(project_name, suffix=suffix_name)
    with tempfile.NamedTemporaryFile(
        suffix=".py",
        mode="w",
        dir=temp_dir,
        delete=False
    ) as fhandler:
        fhandler.write(default_content)
        fhandler.flush()
        return temp_dir, fhandler.name


def run_application(
        application_group_name: str,
        context: ContextItem,
        app_args: Optional[List[str]] = None,
        app_application_variant: Optional[str] = None,
        log_file: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        temporary_directory: Optional[str] = None
    ) -> subprocess.Popen:
    # Start application.
    app_manager, app = get_application(
        application_group_name,
        application_variant=app_application_variant
    )

    context_kwargs = {
        "project_name": context.project_name,
        "app_args": app_args or [],
        "launch_type": LaunchTypes.automated,
        "env": env,
    }

    # If a TaskItem is not provided, the application will start
    # from project environement and not all of the pre-hooks will
    # be executed. This might result as an incomplete environment.
    if isinstance(context, TaskItem):
        context_kwargs.update({
            "folder_path": context.folder_path(),
            "task_name": context.task_name,
            "task_type": context.task_type,
        })

    launch_context = app_manager.create_launch_context(
        app.full_name,
        **context_kwargs,
    )
    launch_context.run_prelaunch_hooks()

    log_file = log_file or os.devnull

    launch_args = launch_context.launch_args
    kwargs = launch_context.kwargs
    kwargs.update({
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    })

    try:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"command line: {launch_args}\n")
            env_log = json.dumps(env or dict(os.environ), indent=4)
            f.write(f"environment: {env_log}\n")
            process = subprocess.Popen(launch_args, **kwargs)

            with force_stdout_utf8():
                for cha_ in iter(lambda: process.stdout.read(1), b""):
                    sys.stdout.write(cha_)
                    f.write(cha_)

                    if process.poll() is not None and cha_ == '':
                        break

            process.wait()

    finally:
        if temporary_directory:
            shutil.rmtree(temporary_directory)

        # TODO: check this, how can we interceipt errors.
        # on Linux returncode is 0 even if Blender render crash with memory.
        if bool(process.returncode):
            f.write(f"Process failed with returncode: {process.returncode}\n")
            cmd_line = " ".join(launch_context.launch_args)
            raise RuntimeError(
                f"Command line failed: {cmd_line} "
                f"with return code: {process.returncode}"
            )

    return process
