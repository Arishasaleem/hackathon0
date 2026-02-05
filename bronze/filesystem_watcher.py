# filesystem_watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil
import time
import logging
from base_watcher import BaseWatcher

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'

    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        dest = self.needs_action / f'FILE_{source.name}'
        shutil.copy2(source, dest)
        self.create_metadata(source, dest)

    def create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        meta_path.write_text(f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
---

New file dropped for processing.
''')

class FilesystemWatcher(BaseWatcher):
    def __init__(self, vault_path: str, watch_path: str):
        super().__init__(vault_path, check_interval=10)  # More frequent for file system
        self.watch_path = Path(watch_path)
        self.observer = Observer()

    def start_watching(self):
        """Start the filesystem watcher"""
        event_handler = DropFolderHandler(self.vault_path)
        self.observer.schedule(event_handler, str(self.watch_path), recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def check_for_updates(self) -> list:
        # This is handled by the event handler, but we keep this for interface compliance
        return []

    def create_action_file(self, item) -> Path:
        # This is handled by the event handler, but we keep this for interface compliance
        pass