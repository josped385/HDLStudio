class Extension:
    """Base class for all HDLStudio extensions."""

    def __init__(self, api):
        self.api = api

    def on_load(self):
        """Called after the extension is loaded and registered."""

    def on_unload(self):
        """Called when the extension is being unloaded."""

    def on_settings_changed(self, key, value):
        """Called when a setting managed by this extension changes."""
