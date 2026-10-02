""" Node collection for the workflow plugin.
"""
import importlib.util
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pathlib import Path

from ayon_workflow.plugin_system import (
    WorkflowNode,
    ExecutionScope,
)
from ayon_workflow.version import __version__ as core_version


def _check_compatibility():
    """ Detect incompatible `ayon_workflow` (core) version.
    """
    package_path = Path(__file__).resolve().parent.parent / "package.py"
    spec = importlib.util.spec_from_file_location(
        "ayon_workflow_nodes_package", package_path
    )
    package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package)

    ayon_workflow_compatible = package.ayon_compatible_addons["workflow"]
    if Version(core_version) not in SpecifierSet(ayon_workflow_compatible):
        raise RuntimeError(
            f"ayon-workflow-nodes-{package.version} requires ayon_workflow-"
            f"{ayon_workflow_compatible}, but found {core_version}."
        )


_check_compatibility()


def get_plugins(
        execution_scope: ExecutionScope = ExecutionScope.WORKSTATION
    ) -> list[WorkflowNode]:
    """
    Returns a list of workflow nodes available in this plugin.
    """
    from .conditions import If

    from .essentials.add_comment import AddComment
    from .essentials.append import Append
    from .essentials.assign_users import AssignUsers
    from .essentials.context import Context
    from .essentials.create_task import CreateTask
    from .essentials.get_parent_context import GetParentContext
    from .essentials.get_version_task import GetVersionTask
    from .essentials.image_sequence import ImageSequenceNode
    from .essentials.merge_sequence import MergeSequence
    from .essentials.no_op import NoOp
    from .essentials.set_attribute import SetAttribute
    from .essentials.set_entity_watchers import SetEntityWatchers
    from .essentials.set_status import SetStatus
    from .essentials.task_context import TaskContext
    from .essentials.video import VideoNode

    from .inputs.cron import OnSchedule
    from .inputs.events import (
        OnVersionCreated,
        OnTaskAssigneesChanged,
        OnStatusChanged,
        OnActionFromFolder,
        OnActionFromVersion,
    )

    from .ui_test import UITest

    nodes = [
        NoOp,
        Append,
        If,
        Context,
        TaskContext,
        GetParentContext,
        GetVersionTask,
        VideoNode,
        ImageSequenceNode,
        MergeSequence,
        SetEntityWatchers,
        SetStatus,
        SetAttribute,
        AssignUsers,
        CreateTask,
        AddComment,
        OnVersionCreated,
        OnTaskAssigneesChanged,
        OnStatusChanged,
        OnActionFromFolder,
        OnActionFromVersion,
        OnSchedule,
    ]

    if execution_scope == ExecutionScope.WORKSTATION:

        from .applications.nuke import NukeRender
        from .applications.blender_render import BlenderRender
        from .applications.blender_workfile import BlenderWorkfile

        from .publish.publish import Publish
        from .publish.representation import Representation

        nodes.extend(
            [
                NukeRender,
                BlenderRender,
                BlenderWorkfile,
                Publish,
                Representation,

                # widget showcase for the desktop editor
                UITest
            ]
        )

    return nodes

__all__ = ["get_plugins"]
