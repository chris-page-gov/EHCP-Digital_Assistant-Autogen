import os
import asyncio
import importlib
import types
import json
import tempfile
from pathlib import Path

import config as original_config

# Utilities to write feedback files for iterations


def make_feedback(path: str, critical: int, major: int = 0, minor: int = 0):
    content = f"""[FEEDBACK_SUMMARY]\nCritical: {critical}\nMajor: {major}\nMinor: {minor}\n[END_FEEDBACK_SUMMARY]\n"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


class StubPromptWriter:  # type: ignore[misc]
    async def a_generate_reply(self, messages):  # minimal duck-typed interface
        return "[REVISION_REQUEST]\n**Document to Revise:**\n(old)\n\n**Revision Instructions:**\n- Improve clarity."

# --- Test process_section control flow by replacing writer + validation behaviour ---


async def run_process_section_under_test():
    import orchestrator

    # Ensure output dir
    os.makedirs(original_config.OUTPUTS_DIR, exist_ok=True)

    # Prepare iteration state
    iteration_state = {"iteration": 0}

    # Monkeypatch orchestrator.create_writer_team (imported symbol) to return stub with required interface
    def fake_create_writer_team(llm_config, llm_config_fast):
        class FakeAgent:
            def __init__(self, name):
                self.name = name

            async def a_initiate_chat(self, recipient, message, clear_history=True):
                # simulate writing a draft file each iteration
                out_path = os.path.join(
                    original_config.OUTPUTS_DIR, "output_s1.md")
                Path(out_path).write_text(
                    f"Draft iteration {iteration_state['iteration']+1}")

        class FakeGroupChat:
            def __init__(self):
                self._agents = {
                    "Writer_User_Proxy": FakeAgent("Writer_User_Proxy")}

            def agent_by_name(self, name):
                return self._agents[name]

        class FakeManager:
            def __init__(self):
                self.groupchat = FakeGroupChat()
        return FakeManager()

    # Monkeypatch validation to write feedback with critical issue first loop then none second loop
    async def fake_run_validation_async(section_number, llm_config, llm_config_fast):
        from utils import save_markdown_file_async
        iteration_state['iteration'] += 1
        feedback_path = os.path.join(
            original_config.OUTPUTS_DIR, f"feedback_s{section_number}.md")
        critical = 1 if iteration_state['iteration'] == 1 else 0
        content = f"[FEEDBACK_SUMMARY]\nCritical: {critical}\nMajor: 0\nMinor: 0\n[END_FEEDBACK_SUMMARY]\n"
        await save_markdown_file_async(feedback_path, content)

    # Apply patches
    orchestrator.create_writer_team = fake_create_writer_team  # type: ignore
    orchestrator.run_validation_async = fake_run_validation_async  # type: ignore

    semaphore = asyncio.Semaphore(1)
    from specialist_agents import create_prompt_writer_agent
    prompt_writer = StubPromptWriter()
    dummy_llm = {"config_list": [
        {"model": "dummy-model", "api_key": "dummy", "base_url": "http://localhost"}]}
    # type: ignore[arg-type]
    result = await orchestrator.process_section("1", semaphore, dummy_llm, dummy_llm, prompt_writer)
    return result


async def test_process_section_passes():
    # Clean previous artifacts
    for f in ["output_s1.md", "feedback_s1.md"]:
        p = Path(original_config.OUTPUTS_DIR)/f
        if p.exists():
            p.unlink()
    assert await run_process_section_under_test() is True

# --- Test main.main_async success / failure branches ---


async def test_main_async_success(monkeypatch, tmp_path):
    import main
    import utils
    # Redirect critical directories to tmp to avoid clobbering real outputs
    monkeypatch.setattr(original_config, "OUTPUTS_DIR",
                        str(tmp_path/"outputs"))
    monkeypatch.setattr(original_config, "PROCESSED_DOCS_DIR",
                        str(tmp_path/"processed_docs"))
    monkeypatch.setattr(original_config, "DOCS_DIR", str(tmp_path/"docs"))
    monkeypatch.setattr(original_config, "LOGS_DIR", str(tmp_path/"logs"))
    os.makedirs(original_config.OUTPUTS_DIR, exist_ok=True)

    # Force single section
    monkeypatch.setattr(original_config, "TOTAL_SECTIONS", 1)

    # Patch heavy functions
    monkeypatch.setattr(utils, "preprocess_all_pdfs", lambda: True)
    monkeypatch.setattr(main, "process_section", lambda *a, **k: True)
    # Create dummy final doc and template after merge step

    def fake_merge(num_sections, out_dir, filename):
        Path(out_dir, f"output_s1.md").write_text("**Name:** Example\n")
        Path(out_dir, filename).write_text("**Name:** Example\n")
        return True
    monkeypatch.setattr(utils, "merge_output_files", fake_merge)
    monkeypatch.setattr(utils, "generate_word_document", lambda *a, **k: None)

    await main.main_async()  # Should run without exceptions


async def test_main_async_failure(monkeypatch, tmp_path):
    import main
    import utils
    monkeypatch.setattr(original_config, "OUTPUTS_DIR",
                        str(tmp_path/"outputs2"))
    monkeypatch.setattr(original_config, "PROCESSED_DOCS_DIR",
                        str(tmp_path/"processed_docs2"))
    monkeypatch.setattr(original_config, "DOCS_DIR", str(tmp_path/"docs2"))
    monkeypatch.setattr(original_config, "LOGS_DIR", str(tmp_path/"logs2"))
    os.makedirs(original_config.OUTPUTS_DIR, exist_ok=True)
    monkeypatch.setattr(original_config, "TOTAL_SECTIONS", 1)
    import orchestrator
    # Force preprocess success but section failure
    monkeypatch.setattr(__import__('utils'),
                        "preprocess_all_pdfs", lambda: True)
    monkeypatch.setattr(main, "process_section", lambda *a, **k: False)
    await main.main_async()  # Should mark failure path


async def test_main_async_merge_failure(monkeypatch, tmp_path):
    import main
    import utils
    monkeypatch.setattr(original_config, "OUTPUTS_DIR", str(tmp_path/"o3"))
    monkeypatch.setattr(
        original_config, "PROCESSED_DOCS_DIR", str(tmp_path/"p3"))
    monkeypatch.setattr(original_config, "DOCS_DIR", str(tmp_path/"d3"))
    os.makedirs(original_config.OUTPUTS_DIR, exist_ok=True)
    monkeypatch.setattr(original_config, "TOTAL_SECTIONS", 1)
    monkeypatch.setenv("NEW_ENGINE", "false")
    monkeypatch.setattr(utils, "preprocess_all_pdfs", lambda: True)
    monkeypatch.setattr(main, "process_section", lambda *a, **k: True)
    # Force merge failure
    monkeypatch.setattr(utils, "merge_output_files", lambda *a, **k: False)
    monkeypatch.setattr(utils, "generate_word_document", lambda *a, **k: None)
    await main.main_async()


async def test_main_async_generate_word_exception(monkeypatch, tmp_path):
    import main
    import utils
    monkeypatch.setattr(original_config, "OUTPUTS_DIR", str(tmp_path/"o4"))
    monkeypatch.setattr(
        original_config, "PROCESSED_DOCS_DIR", str(tmp_path/"p4"))
    monkeypatch.setattr(original_config, "DOCS_DIR", str(tmp_path/"d4"))
    os.makedirs(original_config.OUTPUTS_DIR, exist_ok=True)
    monkeypatch.setattr(original_config, "TOTAL_SECTIONS", 1)
    monkeypatch.setenv("NEW_ENGINE", "false")
    monkeypatch.setattr(utils, "preprocess_all_pdfs", lambda: True)
    monkeypatch.setattr(main, "process_section", lambda *a, **k: True)

    def good_merge(num_sections, out_dir, filename):
        Path(out_dir, "output_s1.md").write_text("**K:** V\n")
        Path(out_dir, filename).write_text("**K:** V\n")
        return True
    monkeypatch.setattr(utils, "merge_output_files", good_merge)
    monkeypatch.setattr(utils, "generate_word_document", lambda *a,
                        **k: (_ for _ in ()).throw(RuntimeError("doc fail")))
    await main.main_async()


async def test_orchestrator_process_section_exception(monkeypatch, tmp_path):
    import orchestrator
    # Force exception inside loop to hit except path

    async def bad_create_writer_team(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(orchestrator, "create_writer_team",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    # patch validation to no-op
    monkeypatch.setattr(
        orchestrator, "run_validation_async", lambda *a, **k: None)
    sem = __import__('asyncio').Semaphore(1)
    prompt_writer = type(
        'PW', (), {"a_generate_reply": lambda self, messages: "[REVISION_REQUEST]"})()
    assert await orchestrator.process_section("1", sem, {}, {}, prompt_writer) is False

# --- Config branch coverage ---


def test_config_azure_branch(monkeypatch):
    # Reload config with Azure vars (disable ollama)
    for k, v in {
        "USE_OLLAMA": "false",
        "AZURE_OPENAI_API_KEY": "key",
        "AZURE_OPENAI_ENDPOINT": "https://example-endpoint/",
        "AZURE_OPENAI_MODEL_NAME": "modelA",
        "AZURE_OPENAI_MODEL_NAME2": "modelB",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview"
    }.items():
        monkeypatch.setenv(k, v)
    import importlib
    cfg = importlib.reload(__import__('config'))
    assert cfg.llm_config['config_list'][0]['api_type'] == 'azure'


async def test_run_validation_async_stub(monkeypatch, tmp_path):
    # Directly test tasks.run_validation_async with monkeypatched validator team
    import tasks
    import validator
    out_dir = original_config.OUTPUTS_DIR
    os.makedirs(out_dir, exist_ok=True)

    class FakeAgent:
        def __init__(self):
            self.name = "Validator_User_Proxy"

        async def a_initiate_chat(self, recipient, message, clear_history=True):
            # simulate document and feedback creation
            Path(os.path.join(out_dir, "output_s1.md")).write_text("Draft")
            make_feedback(os.path.join(out_dir, "feedback_s1.md"), critical=0)

    class FakeGroupChat:
        def __init__(self):
            self._agent = FakeAgent()

        def agent_by_name(self, name):
            return self._agent

    class FakeManager:
        def __init__(self):
            self.groupchat = FakeGroupChat()
    # Need to patch both the symbol in validator module AND the already-imported
    # reference inside tasks (tasks imported create_validator_team directly).
    fake_factory = lambda *a, **k: FakeManager()
    monkeypatch.setattr(validator, "create_validator_team", fake_factory)
    monkeypatch.setattr(tasks, "create_validator_team", fake_factory)
    await tasks.run_validation_async("1", {}, {})
    assert (Path(out_dir)/"feedback_s1.md").exists()
