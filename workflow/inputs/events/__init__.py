""" Event-based input nodes.
"""
from .base import EventTrigger
from .entity_version_created import EntityVersionCreated


__all__ = [
    "EventTrigger",
    "EntityVersionCreated",
]
