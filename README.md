# AYON Workflow Nodes

Vanilla node plugin library for [`ayon-workflow`](https://github.com/ynput/ayon-workflow),
AYON's node-based automation addon.

> [!WARNING]
> This repo only contains **node definitions** (Python plugin classes). The
> graph editor, execution engine and CLI live in `ayon-workflow` itself —
> this package is loaded *by* it and has no standalone use.


## Layout

```
demo/                     # standalone scripts building/running workflows
workflow/
├── __init__.py       # get_plugins() entrypoint discovered by ayon-workflow
├── essentials/        # generic utility nodes
├── conditions/         # branching nodes
├── inputs/             # trigger / input nodes (cron, AYON events, simple actions)
├── applications/       # DCC integrations (Blender, Nuke)
└── publish/            # publishing nodes
publish/
└── collect_instances.py  # pyblish plugin used by the Publish node
```

## Usage

Nodes are consumed through `ayon-workflow`, not imported directly.
Once both packages are installed:

```python
from ayon_workflow.plugin_system import register_all_plugins
from ayon_workflow.workflow_editor import Workflow
from ayon_workflow.workflow_execution import execute_workflow

register_all_plugins()  # discovers get_plugins() from every installed addon

workflow = Workflow(name="my_workflow")
node = workflow.execution_graph.create_node("NoOp")
node["input_data"] = "hello world"

print(execute_workflow(workflow))
```

## Workflow Examples

See [`demo/`](demo/) for more complete, runnable examples:
Run one via the AYON executable, or paste its content into the AYON Console.

```
$AYON_EXECUTABLE run demo/example.py
```

See [`demo/workflow_from_events/`](demo/workflow_from_events/) for
workflows triggered by a cron schedule, an AYON event, or a simple action
instead of run manually.

## Adding Nodes

See [`docs/node_authoring.md`](docs/node_authoring.md) for the node plugin
API and authoring rules.

> [!NOTE]
> We recommend you do not fork this repository to add your own nodes, but
> create your own dedicated addon instead.
