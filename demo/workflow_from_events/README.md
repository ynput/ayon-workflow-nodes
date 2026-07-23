1. Register this directory within the addon settings:
```
{
  "simple_actions": [
    {
      "enabled": true,
      "local": true,
      "workflow_name": "SimpleActionWorkflow",
      "label": "My custom Workflow trigger",
      "input_entity": "Folder"
    }
  ],
  "workflow_directory": "C:\\path\\to\\ayon-workflow\\client\\ayon_workflow\\demo\\workflow_from_events"
}
```
2. This register this 3 workflows from the directory:
* `trigger_from_cron`: Autmatically triggered from cron expression every minute.
* `trigger_from_version_created_event`: Triggered from external event when a new version is created.
* `trigger_from_simple_action`: Triggered from the `SimpleActionWorkflow` simple action defined in settings (locally or remotely).
