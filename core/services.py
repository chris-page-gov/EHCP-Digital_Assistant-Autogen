from __future__ import annotations
import os
from typing import Dict
import config
from .interfaces import IWriterService, IValidatorService, IDocumentStore, IFeedbackParser

# retained for backward compatibility; not authoritative
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# ------------------ Dry-Run Implementations ------------------


class WriterServiceDryRun(IWriterService):
    def __init__(self, store: IDocumentStore):
        self.store = store

    async def write_section(self, section: str, iteration: int) -> None:
        paths = config.get_path_config(section)
        output_path = paths["output"]
        content = f"# Section {section} Draft\nIteration: {iteration}\n"
        self.store.write(output_path, content)


class ValidatorServiceDryRun(IValidatorService):
    def __init__(self, store: IDocumentStore):
        self.store = store

    async def validate_section(self, section: str, iteration: int) -> None:
        paths = config.get_path_config(section)
        feedback_path = paths["feedback"]
        critical = 1 if iteration == 1 else 0
        feedback = (
            "[FEEDBACK_SUMMARY]\n"
            f"Critical: {critical}\nMajor: 0\nMinor: 0\n"
            "[END_FEEDBACK_SUMMARY]\n"
        )
        self.store.write(feedback_path, feedback)

# ------------------ AutoGen-backed Implementations ------------------


class WriterServiceAutoGen(IWriterService):
    """Adapter that reuses existing writer team + prompt writer logic."""

    def __init__(self, store: IDocumentStore, llm_config: dict, llm_config_fast: dict):
        from specialist_agents import create_prompt_writer_agent
        self.store = store
        self.llm_config = llm_config
        self.llm_config_fast = llm_config_fast
        self.prompt_writer = create_prompt_writer_agent(llm_config_fast)

    async def _build_revision_request(self, section: str) -> str:
        paths = config.get_path_config(section)
        output_path = paths["output"]
        feedback_path = paths["feedback"]
        previous = self.store.read(output_path)
        feedback = self.store.read(feedback_path)
        prompt = f"Here is a document that failed validation and the feedback report. Create a clean [REVISION_REQUEST].\n\n**Document to Revise:**\n{previous}\n\n**Feedback Report:**\n{feedback}\n"
        clean_request = await self.prompt_writer.a_generate_reply(messages=[{"role": "user", "content": prompt}])
        if not isinstance(clean_request, str):  # defensive: some wrappers return dict
            clean_request = str(clean_request)
        return clean_request

    async def write_section(self, section: str, iteration: int) -> None:
        from writer import create_writer_team
        from tasks import get_creation_task, get_correction_task
        paths = config.get_path_config(section)
        if iteration == 1:
            task = get_creation_task(section)
        else:
            clean_request = await self._build_revision_request(section)
            task = get_correction_task(section, clean_request)
        manager = create_writer_team(self.llm_config, self.llm_config_fast)
        proxy = manager.groupchat.agent_by_name(
            "Writer_User_Proxy")  # type: ignore[attr-defined]
        # type: ignore[attr-defined]
        await proxy.a_initiate_chat(recipient=manager, message=task, clear_history=True)


class ValidatorServiceAutoGen(IValidatorService):
    def __init__(self, llm_config: dict, llm_config_fast: dict):
        self.llm_config = llm_config
        self.llm_config_fast = llm_config_fast

    async def validate_section(self, section: str, iteration: int) -> None:
        from tasks import run_validation_async
        await run_validation_async(section, self.llm_config, self.llm_config_fast)


def build_services(store: IDocumentStore) -> tuple[IWriterService, IValidatorService]:
    """Factory that chooses dry-run vs real services at call time.

    Reads the DRY_RUN environment variable dynamically so tests can toggle
    behaviour between calls without needing to reload the module.
    """
    if os.getenv("DRY_RUN", "false").lower() == "true":
        return WriterServiceDryRun(store), ValidatorServiceDryRun(store)
    return (
        WriterServiceAutoGen(store, config.llm_config, config.llm_config_fast),
        ValidatorServiceAutoGen(config.llm_config, config.llm_config_fast),
    )


class FeedbackParserAdapter(IFeedbackParser):
    def count_issues(self, feedback: str) -> dict:
        from utils import parse_feedback_and_count_issues
        return parse_feedback_and_count_issues(feedback)
