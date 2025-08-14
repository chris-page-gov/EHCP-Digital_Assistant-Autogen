from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Dict, Optional
from .interfaces import IWriterService, IValidatorService, IDocumentStore, IFeedbackParser
from .evaluator import SectionEvaluator


@dataclass
class SectionRunResult:
    section: str
    iterations: int
    success: bool
    final_issues: Dict[str, int]


class SectionRunner:
    def __init__(self, *, section: str, writer: IWriterService, validator: IValidatorService,
                 store: IDocumentStore, feedback_parser: IFeedbackParser, evaluator: SectionEvaluator,
                 output_path: str, feedback_path: str):
        self.section = section
        self.writer = writer
        self.validator = validator
        self.store = store
        self.feedback_parser = feedback_parser
        self.evaluator = evaluator
        self.output_path = output_path
        self.feedback_path = feedback_path

    async def run(self) -> SectionRunResult:
        iteration = 0
        last_issues = {"critical": 0, "major": 0, "minor": 0}
        while True:
            iteration += 1
            await self.writer.write_section(self.section, iteration)
            await self.validator.validate_section(self.section, iteration)
            feedback_content = self.store.read(self.feedback_path)
            last_issues = self.feedback_parser.count_issues(feedback_content)
            if self.evaluator.is_success(iteration=iteration, issue_counts=last_issues):
                return SectionRunResult(self.section, iteration, True, last_issues)
            if not self.evaluator.should_continue(iteration=iteration, issue_counts=last_issues):
                return SectionRunResult(self.section, iteration, False, last_issues)
