from extensions.extension_base import Extension


class HelloExtension(Extension):

    def on_load(self):
        self.api.write_ok("Hello extension loaded!")

        self.api.register_action(
            "hello.greet", "Say Hello",
            self._on_hello,
            shortcut=None
        )

        self.api.add_menu_item("Tools", "hello.greet")

        self._count = self.api.get_setting("greet_count", 0)

    def _on_hello(self):
        self._count += 1
        self.api.set_setting("greet_count", self._count)
        self.api.write_console(f"Hello from extension! (x{self._count})")

    def on_unload(self):
        self.api.write_console("Hello extension unloaded")
