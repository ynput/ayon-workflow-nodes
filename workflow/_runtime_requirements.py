"""Runtime dependency helpers for workflow plugins."""

from __future__ import annotations

from typing import Any

_AYON_API_IMPORT_ERROR: ModuleNotFoundError | None = None

try:
    import ayon_api as _ayon_api
except ModuleNotFoundError as exc:
    _ayon_api = None
    _AYON_API_IMPORT_ERROR = exc


def get_ayon_api() -> Any:
    if _ayon_api is not None:
        return _ayon_api

    raise RuntimeError(
        "Built-in Workflow nodes that access AYON data run inside the local "
        "API Python process and require the `ayon-python-api` package "
        "(`import ayon_api`). Install or update that package in this Python "
        "environment, restart the editor/API, and run the workflow again."
    ) from _AYON_API_IMPORT_ERROR
