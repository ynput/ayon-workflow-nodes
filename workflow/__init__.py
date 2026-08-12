""" Node collection for the workflow plugin.
"""
from ayon_workflow.plugin_system.interface import WorkflowNode


def get_plugins() -> list[WorkflowNode]:
    """
    Returns a list of workflow nodes available in this plugin.
    """

    from .applications.nuke import NukeRender
    from .applications.blender_render import BlenderRender
    from .applications.blender_workfile import BlenderWorkfile

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

    from .publish.publish import Publish
    from .publish.representation import Representation

    from .ui_test import UITest

    return [
        NoOp,
        Append,
        If,
        Context,
        TaskContext,
        VideoNode,
        ImageSequenceNode,
        MergeSequence,
        NukeRender,
        BlenderRender,
        BlenderWorkfile,
        Publish,
        Representation,
        UITest,
        OnVersionCreated,
        OnActionFromFolder,
        OnActionFromVersion,
        OnSchedule,
    ]


__all__ = ["get_plugins"]
