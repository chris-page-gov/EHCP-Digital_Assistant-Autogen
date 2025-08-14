from __future__ import annotations
from typing import Protocol, Iterable, Dict, Any, Optional


class ILLMClient(Protocol):
    async def generate(
        self, *, messages: list[dict], role: str, **kwargs) -> str: ...


class IWriterService(Protocol):
    async def write_section(self, section: str, iteration: int) -> None: ...


class IValidatorService(Protocol):
    async def validate_section(self, section: str, iteration: int) -> None: ...


class IDocumentStore(Protocol):
    def read(self, path: str) -> str: ...
    def exists(self, path: str) -> bool: ...
    def write(self, path: str, content: str) -> None: ...


class IFeedbackParser(Protocol):
    def count_issues(self, feedback: str) -> dict: ...


class ISectionEvaluator(Protocol):
    def should_continue(self, *, iteration: int,
                        issue_counts: dict) -> bool: ...

    def is_success(self, *, iteration: int, issue_counts: dict) -> bool: ...
