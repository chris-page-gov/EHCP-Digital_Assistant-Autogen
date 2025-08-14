from __future__ import annotations
import os
from typing import Dict


class InMemoryDocumentStore:
    def __init__(self):
        self._data: Dict[str, str] = {}

    def read(self, path: str) -> str:
        return self._data.get(path, "")

    def write(self, path: str, content: str) -> None:
        self._data[path] = content

    def exists(self, path: str) -> bool:
        return path in self._data


class FileSystemDocumentStore:
    def read(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def write(self, path: str, content: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def exists(self, path: str) -> bool:
        return os.path.exists(path)
