""" Event-based input nodes.
"""
from .base import EventTrigger
from .entity_version_created import OnVersionCreated
from .entity_task_assignees_changed import OnTaskAssigneesChanged
from .entity_status_changed import OnStatusChanged
from .simple_actions import OnActionFromFolder, OnActionFromVersion


__all__ = [
    "OnActionFromFolder",
    "OnActionFromVersion",
    "EventTrigger",
    "OnVersionCreated",
    "OnTaskAssigneesChanged",
    "OnStatusChanged",
]
