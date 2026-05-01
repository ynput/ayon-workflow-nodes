"""Execution helpers for Python workflow nodes."""

from __future__ import annotations

import contextlib
import dataclasses
import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Optional

DEFAULT_SCRIPT = """\
# New Python nodes start with a removable custom input named 'input'
# and a removable custom output named 'output'.
print(f"input = {input!r}")

# Any additional custom input ports are also exposed as named variables.
# Example: if you add a port called "source_path", you can use source_path here.

# --- your work here ---
result = input

# Assign a dict to 'outputs' keyed by your custom output port names.
outputs = {"output": result}
"""

_WRAPPER_SCRIPT = """\
import json
import os
import runpy

inputs_path = os.environ.get("AYON_WF_INPUTS")
if inputs_path and os.path.isfile(inputs_path):
    with open(inputs_path, encoding="utf-8") as stream:
        inputs = json.load(stream)
else:
    inputs = []

named_inputs_path = os.environ.get("AYON_WF_NAMED_INPUTS")
if named_inputs_path and os.path.isfile(named_inputs_path):
    with open(named_inputs_path, encoding="utf-8") as stream:
        named_inputs = json.load(stream)
else:
    named_inputs = {}

namespace = runpy.run_path(
    os.environ["AYON_WF_SCRIPT"],
    init_globals={
        "inputs": inputs,
        "outputs": None,
        **named_inputs,
    },
    run_name="__main__",
)

outputs_path = os.environ.get("AYON_WF_OUTPUTS")
if outputs_path:
    with open(outputs_path, "w", encoding="utf-8") as stream:
        json.dump(namespace.get("outputs"), stream)
"""


@contextlib.contextmanager
def force_stdout_utf8():
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if not callable(reconfigure):
        yield
        return

    original_encoding = sys.stdout.encoding
    original_errors = sys.stdout.errors

    reconfigure(encoding="utf-8", errors="replace")
    try:
        yield
    finally:
        reconfigure(
            encoding=original_encoding or "utf-8",
            errors=original_errors or "strict",
        )


def run_python_uv(
    snippet: str,
    requirements: Optional[list[str]] = None,
    python_version: Optional[str] = None,
    inputs: Optional[Any] = None,
    **named_inputs: Any,
) -> Any:
    """Execute a Python snippet in an isolated uv-managed environment."""
    paths = _create_temp_context(snippet, inputs, named_inputs)
    try:
        command = ["uv", "run"]
        if python_version and python_version.strip():
            command.extend(["--python", python_version.strip()])

        for requirement in requirements or []:
            requirement = requirement.strip()
            if requirement:
                command.extend(["--with", requirement])

        command.append(paths["wrapper"])
        _run_subprocess(
            command,
            env=_build_env(paths),
            missing_binary_message=(
                "uv is required to execute PythonUV nodes."
            ),
            failure_label="uv Python snippet",
        )
        return _read_outputs(paths["outputs"])
    finally:
        _cleanup(paths)


def run_python_ayon(
    snippet: str,
    inputs: Optional[Any] = None,
    **named_inputs: Any,
) -> Any:
    """Execute a Python snippet using AYON's Python runtime."""
    try:
        from ayon_core.lib import get_ayon_launcher_args
    except ImportError as exc:
        raise RuntimeError(
            "AYON Python execution is not available in this environment."
        ) from exc

    paths = _create_temp_context(snippet, inputs, named_inputs)
    try:
        command = list(get_ayon_launcher_args("run", paths["wrapper"]))
        _run_subprocess(
            command,
            env=_build_env(paths),
            missing_binary_message=(
                "AYON launcher arguments could not be resolved for "
                "PythonAYON nodes."
            ),
            failure_label="AYON Python snippet",
        )
        return _read_outputs(paths["outputs"])
    finally:
        _cleanup(paths)


def _normalize_inputs(inputs: Optional[Any]) -> list[Any]:
    if inputs is None:
        return []
    if isinstance(inputs, list):
        return inputs
    if isinstance(inputs, tuple):
        return list(inputs)
    return [inputs]


def _create_temp_context(
    snippet: str,
    inputs: Optional[Any],
    named_inputs: Optional[dict[str, Any]],
) -> dict[str, str]:
    paths: dict[str, str] = {}
    normalized_inputs = _normalize_inputs(inputs)
    try:
        paths["script"] = _mktemp(".py", snippet)
        paths["wrapper"] = _mktemp(".py", _WRAPPER_SCRIPT)
        paths["inputs"] = _mktemp(
            ".json",
            json.dumps(_serialize(normalized_inputs)),
        )
        paths["named_inputs"] = _mktemp(
            ".json",
            json.dumps(_serialize(named_inputs or {})),
        )
        paths["outputs"] = _mktemp(".json", "null")
    except Exception:
        _cleanup(paths)
        raise
    return paths


def _build_env(paths: dict[str, str]) -> dict[str, str]:
    return {
        **os.environ,
        "AYON_WF_SCRIPT": paths["script"],
        "AYON_WF_INPUTS": paths["inputs"],
        "AYON_WF_NAMED_INPUTS": paths["named_inputs"],
        "AYON_WF_OUTPUTS": paths["outputs"],
    }


def _run_subprocess(
    command: list[str],
    *,
    env: dict[str, str],
    missing_binary_message: str,
    failure_label: str,
) -> None:
    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }

    try:
        process = subprocess.Popen(command, env=env, **kwargs)
    except FileNotFoundError as exc:
        raise RuntimeError(missing_binary_message) from exc

    stdout = process.stdout
    if stdout is None:
        raise RuntimeError(f"Could not capture output for {failure_label}.")

    with force_stdout_utf8():
        for line in stdout:
            sys.stdout.write(line)

    return_code = process.wait()
    if return_code:
        raise RuntimeError(
            f"{failure_label} exited with code {return_code}."
        )


def _read_outputs(outputs_path: str) -> Any:
    try:
        with open(outputs_path, encoding="utf-8") as stream:
            return json.load(stream)
    except OSError as exc:
        raise RuntimeError(
            f"Failed to read Python node outputs from '{outputs_path}'."
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Python node outputs were not valid JSON."
        ) from exc


def _cleanup(paths: dict[str, str]) -> None:
    for path in paths.values():
        try:
            os.unlink(path)
        except OSError:
            pass


def _mktemp(suffix: str, content: str) -> str:
    descriptor, path = tempfile.mkstemp(suffix=suffix, prefix="ayon_wf_")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
    except Exception:
        os.unlink(path)
        raise
    return path


def _serialize(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {
            str(key): _serialize(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _serialize(dataclasses.asdict(value))
    if isinstance(value, set):
        return [_serialize(item) for item in sorted(value, key=str)]
    if isinstance(value, Iterable):
        return [_serialize(item) for item in value]
    return str(value)
