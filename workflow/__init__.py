""" Node collection for the workflow plugin.
"""
from ayon_workflow.plugin_system import (
    WorkflowNode,
    ExecutionScope,
)


def get_plugins(
        execution_scope: ExecutionScope = ExecutionScope.WORKSTATION
    ) -> list[WorkflowNode]:
    """
    Returns a list of workflow nodes available in this plugin.
    """
    from .conditions import If

    from .essentials.append import Append
    from .essentials.context import Context
    from .essentials.image_sequence import ImageSequenceNode
    from .essentials.merge_sequence import MergeSequence
    from .essentials.no_op import NoOp
    from .essentials.task_context import TaskContext
    from .essentials.video import VideoNode

    from .inputs.cron import OnSchedule
    from .inputs.events import (
        OnVersionCreated,
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
        VideoNode,
        ImageSequenceNode,
        MergeSequence,
        UITest,
        OnVersionCreated,
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
            ]
        )

    return nodes


__all__ = ["get_plugins"]
