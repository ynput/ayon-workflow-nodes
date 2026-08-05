1. Register this directory within the addon settings:
```
{
  "simple_actions": [
    {
      "enabled": true,
      "local": true,
      "workflow_name": "SimpleActionWorkflowFolder",
      "label": "My custom Folder trigger",
      "input_entity": "Folder"
    }
  ],
  "workflow_directory": "C:\\path\\to\\ayon-workflow\\client\\ayon_workflow\\demo\\workflow_from_events"
}
```
2. This register this 3 workflows from the directory, those can be reviewed through the web-editor:
    * `trigger_from_cron`: Autmatically triggered from cron expression every minute.
    * `trigger_from_version_created_event`: Triggered from external event when a new version is created.
    * `trigger_from_simple_action`: Triggered from the `SimpleActionWorkflow` simple action defined in settings (locally or remotely).
3. Prepare a service user and set it token id in the `AYON_WORKFLOW_API_KEY` environment variable.
4. Run the processor through AYON launcher: `$AYON_EXECUTABLE --use-dev --verbose info .\client\ayon_workflow\event_processor.py`
5. Results:
    * Ensure the cron workflow is triggered on its own every minutes.
    * Ensure the simple action workflow is triggered when the simple action is triggered and not local.
    * Ensure the simple action workflow is run locally when the simple action is triggered and local.
    * Ensure the workflow from version created event is triggered when a new version is created.
