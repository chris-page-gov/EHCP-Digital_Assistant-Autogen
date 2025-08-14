from __future__ import annotations
import asyncio
import os
import config
from .store import InMemoryDocumentStore, FileSystemDocumentStore
from .services import build_services, FeedbackParserAdapter
from .evaluator import SectionEvaluator
from .runner import SectionRunner

NEW_ENGINE = os.getenv("NEW_ENGINE", "false").lower() == "true"


async def run_all_sections_new_engine():
    store = FileSystemDocumentStore()
    writer_service, validator_service = build_services(store)
    parser = FeedbackParserAdapter()
    evaluator = SectionEvaluator(max_iterations=config.MAX_SECTION_ITERATIONS)

    tasks = []
    for i in range(1, config.TOTAL_SECTIONS + 1):
        section = str(i)
        paths = config.get_path_config(section)
        runner = SectionRunner(
            section=section,
            writer=writer_service,
            validator=validator_service,
            store=store,
            feedback_parser=parser,
            evaluator=evaluator,
            output_path=paths["output"],
            feedback_path=paths["feedback"],
        )
        tasks.append(runner.run())
    results = await asyncio.gather(*tasks)
    return results
