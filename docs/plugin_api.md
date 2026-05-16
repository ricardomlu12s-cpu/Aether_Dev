# Plugin API

MVP plugins are discovered by scanning `plugins/*/manifest.json`.

```json
{
  "name": "example_memory_plugin",
  "version": "0.1.0",
  "type": "memory_plugin",
  "entrypoint": "plugin.py",
  "permissions": ["memory:read", "memory:write"],
  "enabled": false,
  "config_schema": {}
}
```

Reserved plugin types:

- memory_plugin
- emotion_plugin
- model_plugin
- perception_plugin
- action_plugin
- ui_plugin

