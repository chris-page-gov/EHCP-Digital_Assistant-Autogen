import os
import importlib
import pytest


@pytest.mark.asyncio
async def test_writer_service_autogen_creation_and_revision(monkeypatch, tmp_path):
    monkeypatch.setenv("DRY_RUN", "false")
    monkeypatch.setenv("USE_OLLAMA", "true")
    import config
    importlib.reload(config)

    # Redirect directories
    monkeypatch.setattr(config, "OUTPUTS_DIR", str(tmp_path/"outputs"))
    monkeypatch.setattr(config, "PROCESSED_DOCS_DIR",
                        str(tmp_path/"processed_docs"))
    monkeypatch.setattr(config, "INSTRUCTIONS_DIR",
                        str(tmp_path/"instructions"))
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DOCS_DIR, exist_ok=True)
    os.makedirs(config.INSTRUCTIONS_DIR, exist_ok=True)

    # Guidance + partials
    (tmp_path/"instructions"/"writer_guidance_s1.md").write_text("writer guidance")
    (tmp_path/"instructions"/"validation_guidance_s1.md").write_text("validator guidance")
    partials = tmp_path/"instructions"/"partials"
    os.makedirs(partials, exist_ok=True)
    for name in [
        "_writer_common_rules.md",
        "_validator_common_feedback_format.md",
        "_need_categorisation_guide.md",
        "_need_provision_outcome_writer_guidance.md",
        "_provision_specificity_rules.md",
        "_smart_outcomes_rules.md",
        "_golden_thread_rules.md",
    ]:
        (partials/name).write_text("rules")

    # Reload config to re-bind partial paths
    importlib.reload(config)

    from core import services as svc
    import specialist_agents
    import writer as writer_module

    # Force non-dry-run
    monkeypatch.setattr(svc, "DRY_RUN", False)

    sent_messages = []

    class FakeProxy:
        async def a_initiate_chat(self, recipient, message, clear_history=True):
            sent_messages.append(message)

    class FakeGroupChat:
        def agent_by_name(self, name):
            return FakeProxy()

    class FakeManager:
        def __init__(self):
            self.groupchat = FakeGroupChat()

    monkeypatch.setattr(writer_module, "create_writer_team",
                        lambda *a, **k: FakeManager())

    class FakePromptAgent:
        async def a_generate_reply(self, messages):
            return {"clean": "Please revise"}

    monkeypatch.setattr(
        specialist_agents, "create_prompt_writer_agent", lambda cfg: FakePromptAgent())

    from core.store import InMemoryDocumentStore
    store = InMemoryDocumentStore()
    writer_service, _ = svc.build_services(store)

    await writer_service.write_section("1", 1)
    assert len(sent_messages) == 1
    assert "generate the summary document" in sent_messages[0]

    paths = config.get_path_config("1")
    store.write(paths["output"], "# Previous Draft\n")
    store.write(
        paths["feedback"], "[FEEDBACK_SUMMARY]\nCritical: 1\nMajor: 0\nMinor: 0\n[END_FEEDBACK_SUMMARY]\n")

    await writer_service.write_section("1", 2)
    assert len(sent_messages) == 2
    assert "Please revise" in sent_messages[1]
    assert "You are the writer team" in sent_messages[1]


@pytest.mark.asyncio
async def test_validator_service_autogen_invokes_run(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "false")
    monkeypatch.setenv("USE_OLLAMA", "true")
    import config
    import importlib
    importlib.reload(config)

    called = {}

    async def fake_run_validation_async(section, llm_config, llm_config_fast):
        called["section"] = section
        called["llm_config"] = llm_config
        called["fast"] = llm_config_fast

    import tasks
    monkeypatch.setattr(tasks, "run_validation_async",
                        fake_run_validation_async)

    from core import services as svc
    monkeypatch.setattr(svc, "DRY_RUN", False)
    validator = svc.ValidatorServiceAutoGen(
        config.llm_config, config.llm_config_fast)
    await validator.validate_section("2", 1)
    assert called["section"] == "2"
    assert called["llm_config"]["config_list"][0]["model"]
    assert called["fast"]["config_list"][0]["model"]
