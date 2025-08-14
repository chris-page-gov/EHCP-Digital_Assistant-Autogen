import pytest
from core.runner import SectionRunner, SectionEvaluator
from core.store import InMemoryDocumentStore


class DummyWriter:
    def __init__(self, store, output_path):
        self.store = store
        self.output_path = output_path

    async def write_section(self, section: str, iteration: int):
        self.store.write(self.output_path, f"Draft {iteration}")


class DummyValidator:
    def __init__(self, store, feedback_path, critical_pattern):
        self.store = store
        self.feedback_path = feedback_path
        self.critical_pattern = critical_pattern

    async def validate_section(self, section: str, iteration: int):
        # Produce critical on iterations matching pattern
        critical = 1 if self.critical_pattern(iteration) else 0
        self.store.write(
            self.feedback_path, f"[FEEDBACK_SUMMARY]\nCritical: {critical}\nMajor: 0\nMinor: 0\n[END_FEEDBACK_SUMMARY]\n")


class Parser:
    def count_issues(self, feedback: str):
        import re
        m = re.search(r"Critical:\s*(\d+)", feedback)
        c = int(m.group(1)) if m else 0
        return {"critical": c, "major": 0, "minor": 0}


@pytest.mark.asyncio
async def test_runner_succeeds_second_iteration():
    store = InMemoryDocumentStore()
    writer = DummyWriter(store, "out.md")
    validator = DummyValidator(
        store, "fb.md", critical_pattern=lambda i: i == 1)
    evaluator = SectionEvaluator(max_iterations=5)
    runner = SectionRunner(section="1", writer=writer, validator=validator, store=store,
                           feedback_parser=Parser(), evaluator=evaluator,
                           output_path="out.md", feedback_path="fb.md")
    res = await runner.run()
    assert res.success is True
    assert res.iterations == 2


@pytest.mark.asyncio
async def test_runner_fails_after_max():
    store = InMemoryDocumentStore()
    writer = DummyWriter(store, "out.md")
    validator = DummyValidator(
        store, "fb.md", critical_pattern=lambda i: True)  # always critical
    evaluator = SectionEvaluator(max_iterations=3)
    runner = SectionRunner(section="2", writer=writer, validator=validator, store=store,
                           feedback_parser=Parser(), evaluator=evaluator,
                           output_path="out.md", feedback_path="fb.md")
    res = await runner.run()
    assert res.success is False
    assert res.iterations == 3


def test_evaluator_rules():
    from core.evaluator import SectionEvaluator
    ev = SectionEvaluator(max_iterations=4)
    # iteration 1 with no critical should NOT be success but continue forced
    assert ev.is_success(iteration=1, issue_counts={"critical": 0}) is False
    assert ev.should_continue(iteration=1, issue_counts={
                              "critical": 0}) is True
    # iteration 2 with critical present should not be success but continue
    assert ev.is_success(iteration=2, issue_counts={"critical": 1}) is False
    assert ev.should_continue(iteration=2, issue_counts={
                              "critical": 1}) is True
    # iteration 2 with no critical meets success rule
    assert ev.is_success(iteration=2, issue_counts={"critical": 0}) is True
    # max iterations reached stops continuation
    assert ev.should_continue(iteration=4, issue_counts={
                              "critical": 1}) is False
