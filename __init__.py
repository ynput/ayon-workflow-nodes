""" ayon-workflow-nodes.
"""
from .package import (
    version as __version__,
    ayon_compatible_addons,
)


def check_compatibility():
    """ Detect incompatible `ayon_workflow` (core) version
    """
    from packaging.specifiers import SpecifierSet
    from packaging.version import Version

    from ayon_workflow.version import __version__ as core_version

    ayon_workflow_compatible = ayon_compatible_addons["workflow"]
    if Version(core_version) not in SpecifierSet(ayon_workflow_compatible):
        raise RuntimeError(
            f"ayon-workflow-nodes-{__version__} requires ayon_workflow-"
            f"{ayon_workflow_compatible}, but found {core_version}."
        )


check_compatibility()
