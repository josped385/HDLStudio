import importlib.util
import json
import os
import sys

from PyQt6.QtCore import QSettings

from extensions.api import ExtensionAPI
from extensions.extension_base import Extension as _BaseExtension


EXTENSIONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "extensions"
)


class ExtensionManager:

    def __init__(self, main_window):
        self._main = main_window
        self._extensions = {}           # ext_id -> Extension instance
        self._apis = {}                 # ext_id -> ExtensionAPI
        self._manifests = {}            # ext_id -> manifest dict
        self._disabled = set()

        self._load_disabled_set()

    # ── Public API ────────────────────────────────────────

    def discover_and_load_all(self):
        if not os.path.isdir(EXTENSIONS_DIR):
            return
        for name in sorted(os.listdir(EXTENSIONS_DIR)):
            ext_dir = os.path.join(EXTENSIONS_DIR, name)
            manifest_path = os.path.join(ext_dir, "manifest.json")
            if not os.path.isfile(manifest_path):
                continue
            if not os.path.isdir(ext_dir):
                continue
            self._load_one(ext_dir)

    def get_extension(self, ext_id):
        return self._extensions.get(ext_id)

    def get_manifest(self, ext_id):
        return self._manifests.get(ext_id)

    def list_extensions(self):
        return [
            {"id": eid, "manifest": self._manifests.get(eid, {}),
             "loaded": eid in self._extensions,
             "disabled": eid in self._disabled}
            for eid in sorted(self._manifests.keys())
        ]

    def is_disabled(self, ext_id):
        return ext_id in self._disabled

    def set_disabled(self, ext_id, disabled):
        if disabled:
            self._disabled.add(ext_id)
            self._unload_one(ext_id)
        else:
            self._disabled.discard(ext_id)
            self._load_one(
                os.path.join(EXTENSIONS_DIR, ext_id)
            )
        self._save_disabled_set()

    def unload_all(self):
        for eid in list(self._extensions.keys()):
            self._unload_one(eid)

    # ── Internal ──────────────────────────────────────────

    def _load_disabled_set(self):
        s = QSettings("HDLStudio", "HDLStudio")
        s.beginGroup("extensions")
        raw = s.value("disabled", "")
        if raw:
            self._disabled = set(raw.split(","))
        s.endGroup()

    def _save_disabled_set(self):
        s = QSettings("HDLStudio", "HDLStudio")
        s.beginGroup("extensions")
        s.setValue("disabled", ",".join(sorted(self._disabled)))
        s.endGroup()

    def _load_one(self, ext_dir):
        ext_id = os.path.basename(ext_dir)
        if ext_id in self._disabled:
            return
        if ext_id in self._extensions:
            return

        manifest_path = os.path.join(ext_dir, "manifest.json")
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as exc:
            self._main.bottom_panel.write_error(
                f"[Extensions] Failed to read manifest for '{ext_id}': {exc}"
            )
            return

        main_module = manifest.get("main", "main.py")
        entry_path = os.path.join(ext_dir, main_module)
        if not os.path.isfile(entry_path):
            self._main.bottom_panel.write_error(
                f"[Extensions] Entry point not found: {entry_path}"
            )
            return

        try:
            spec = importlib.util.spec_from_file_location(
                f"extensions_user.{ext_id}", entry_path
            )
            mod = importlib.util.module_from_spec(spec)
            # Make extension dir importable for relative imports
            if ext_dir not in sys.path:
                sys.path.insert(0, ext_dir)
            spec.loader.exec_module(mod)
        except Exception as exc:
            self._main.bottom_panel.write_error(
                f"[Extensions] Failed to load '{ext_id}': {exc}"
            )
            return

        # Find an Extension subclass
        ext_class = None
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (isinstance(attr, type) and
                    attr.__name__ != "Extension" and
                    issubclass(attr, _BaseExtension)):
                    ext_class = attr
                    break

        if ext_class is None:
            self._main.bottom_panel.write_warning(
                f"[Extensions] No Extension subclass found in '{ext_id}'"
            )
            return

        api = ExtensionAPI(self._main, ext_id)
        instance = ext_class(api)

        self._manifests[ext_id] = manifest
        self._extensions[ext_id] = instance
        self._apis[ext_id] = api

        try:
            instance.on_load()
            self._main.bottom_panel.write_ok(
                f"[Extensions] Loaded '{manifest.get('name', ext_id)}'"
            )
        except Exception as exc:
            self._main.bottom_panel.write_error(
                f"[Extensions] Error in {ext_id}.on_load(): {exc}"
            )
            self._unload_one(ext_id)

    def _unload_one(self, ext_id):
        instance = self._extensions.pop(ext_id, None)
        api = self._apis.pop(ext_id, None)
        if instance is not None:
            try:
                instance.on_unload()
            except Exception as exc:
                self._main.bottom_panel.write_error(
                    f"[Extensions] Error in {ext_id}.on_unload(): {exc}"
                )
        if api is not None:
            api.unregister_all()
        self._manifests.pop(ext_id, None)



