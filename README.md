# AYON Workflow Nodes
 
The official node library for the [AYON Workflow addon](https://help.ayon.app/en/help/collections/6014460-workflow).
 
This repository contains the nodes that ship with the AYON Workflow addon, from
generic utilities and branching logic to event triggers, DCC integrations
(Blender, Nuke), and publishing.
 
> [!IMPORTANT]
> **`ayon-workflow-nodes` is not a standalone package.** It is part of the
> official AYON Workflow addon release and only contains the node definitions
> (Python plugin classes) that ship with the addon.
>
> These nodes are open-sourced so the community can contribute fixes and
> improvements, and so there's a set of real, working examples to learn from
> when writing your own nodes.
>
> This repository is not meant to be forked to add custom workflow nodes.
> Keep custom nodes in your own repository and register them with the Workflow
> addon, either through `AYON_WORKFLOW_ADDITIONAL_PLUGIN_PATH` or by packaging
> them in your own AYON addon, as described in
> [Extending Workflow Nodes (Custom Plugins)](https://docs.ayon.dev/docs/dev_addon_workflow#extending-workflow-nodes-custom-plugins).
 
## Repository Layout
 
```
demo/                        # example workflows, ready to open or run
workflow/
  ├── __init__.py            # get_plugins() entrypoint, discovered by the Workflow addon
  ├── essentials/            # generic utility nodes
  ├── conditions/            # branching nodes
  ├── inputs/                # trigger and input nodes (cron, AYON events, simple actions)
  ├── applications/          # DCC integrations (Blender, Nuke)
  └── publish/               # publishing nodes
publish/
  └── collect_instances.py   # pyblish plugin used by the Publish node
```
 
## Running the Demo Workflows
 
The [`demo/`](demo/) folder holds the example workflows that are distributed
with the addon, so you can grab them here instead of digging through your local
addon folder.
 
**Open in the editor.** Launch the Workflow editor from the AYON tray and load a
demo workflow file via `File > Load...` to inspect, tweak, and run it
interactively. For detailed steps, see
[Workflow Editor: Your First Workflows](https://help.ayon.app/en/help/articles/8963758-workflow-editor-your-first-workflows).
 
**Run from the command line.** For more details, see
[Command-Line Interface (CLI) Execution](https://docs.ayon.dev/docs/dev_addon_workflow#command-line-interface-cli-execution).
 
- Windows:
    ```
    ./ayon_console.exe addon workflow execute --workflow-path /path/to/workflow.json
    ```
- Linux and macOS:
    ```
    ayon addon workflow execute --workflow-path /path/to/workflow.json
    ```
 
**Event-triggered workflows.** For workflows that start on their own, from a
cron schedule, an AYON event, or a simple action, see
[`demo/workflow_from_events/`](demo/workflow_from_events/). For detailed steps
on setting them up, see
[Workflows & Automations](https://help.ayon.app/en/help/articles/1804107-workflows-and-automations).
 
## Contributing
 
Fixes and improvements to the official nodes are welcome. See
[`docs/node_authoring.md`](docs/node_authoring.md) for the node plugin API and
authoring rules.
 
## Further Reading
 
- [Workflow user guides](https://help.ayon.app/en/help/collections/6014460-workflow)
- [Workflow developer docs](https://docs.ayon.dev/docs/dev_addon_workflow)
- [Event-triggered workflows](https://docs.ayon.dev/docs/dev_addon_workflow_event)
- [Workflow addon API reference](https://docs.ayon.dev/ayon-workflow-docs/latest/)