""" Node collection for the workflow plugin.
"""
from ayon_workflow.plugin_system.interface import WorkflowNode


def get_server_plugins() -> list[WorkflowNode]:
    """
    Returns a list of light workflow nodes available in this plugin.
    """
    from .essentials.append import Append
    from .essentials.context import Context
    from .essentials.image_sequence import ImageSequenceNode
    from .essentials.merge_sequence import MergeSequence
    from .essentials.no_op import NoOp
    from .essentials.task_context import TaskContext
    from .essentials.video import VideoNode

    from .inputs.cron import Cron
    from .inputs.events import EntityVersionCreated, ActionFromFolder
    from .publish.representation import Representation

    return [
        NoOp,
        Append,
        Context,
        TaskContext,
        VideoNode,
        ImageSequenceNode,
        MergeSequence,
        Representation,
        EntityVersionCreated,
        Cron,
        ActionFromFolder,
    ]


def get_plugins() -> list[WorkflowNode]:
    """
    Returns a list of workflow nodes available in this plugin.
    """

    from .applications.nuke import NukeRender
    from .applications.blender_render import BlenderRender
    from .applications.blender_workfile import BlenderWorkfile

    from .publish.publish import Publish

    from .ui_test import UITest

    return get_server_plugins() + [
        NukeRender,
        BlenderRender,
        BlenderWorkfile,
        Publish,
        UITest,
    ]


__all__ = ["get_plugins"]
