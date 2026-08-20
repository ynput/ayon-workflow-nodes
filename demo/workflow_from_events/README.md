1. Load and upload the workflows from this directory as new registered workflows (this is done through the web-editor-> File menu)
2. Define a new simple action that is enabled on Folder
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
}
```
3a. Run the processor through AYON launcher: `$AYON_EXECUTABLE --use-dev event-processor`
3b. 1. Build the docker image locally through `Makefile`
    2. Start the service from ASH service

5. Results:
    * Ensure the cron workflow is triggered on its own every minutes.
    * Ensure the simple action workflow is triggered when the simple action is triggered and not local.
    * Ensure the simple action workflow is run locally when the simple action is triggered and local.
    * Ensure the workflow from version created event is triggered when a new version is created.
