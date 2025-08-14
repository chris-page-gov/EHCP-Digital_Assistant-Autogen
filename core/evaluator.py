from __future__ import annotations
from typing import Dict


class SectionEvaluator:
    """Pure evaluation logic for loop control.

    Success rule: no critical issues AND iteration >=2 (force at least two loops)
    Continue rule: iteration < max_iterations AND (critical > 0 or iteration == 1)
    """

    def __init__(self, max_iterations: int):
        self.max_iterations = max_iterations

    def is_success(self, *, iteration: int, issue_counts: Dict[str, int]) -> bool:
        return issue_counts.get('critical', 0) == 0 and iteration >= 2

    def should_continue(self, *, iteration: int, issue_counts: Dict[str, int]) -> bool:
        if iteration >= self.max_iterations:
            return False
        if issue_counts.get('critical', 0) > 0:
            return True
        if iteration == 1:  # force second loop
            return True
        return False
