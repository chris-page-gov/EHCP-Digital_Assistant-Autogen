import os
import asyncio
import pytest
import importlib


@pytest.mark.asyncio
async def test_new_engine_dry_run(monkeypatch, tmp_path):
    monkeypatch.setenv("NEW_ENGINE", "true")
    # Ensure dry-run even if prior tests flipped the env
    monkeypatch.setenv("DRY_RUN", "true")
    # Ensure ollama mode to avoid azure env check
    monkeypatch.setenv("USE_OLLAMA", "true")
    # Reload config to pick up env
    import config
    importlib.reload(config)
    # Redirect key directories
    monkeypatch.setattr(config, "OUTPUTS_DIR", str(tmp_path/"outputs"))
    monkeypatch.setattr(config, "PROCESSED_DOCS_DIR",
                        str(tmp_path/"processed_docs"))
    monkeypatch.setattr(config, "DOCS_DIR", str(tmp_path/"docs"))
    monkeypatch.setattr(config, "FINAL_DOCUMENT_PATH", str(
        tmp_path/"outputs"/"final_document.md"))
    monkeypatch.setattr(config, "FINAL_DOCUMENT_FILENAME", "final_document.md")
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
    # required for preprocess to succeed
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    # Create dummy template
    (tmp_path/"template.docx").write_text("placeholder")
    monkeypatch.setattr(config, "BASE_DIR", str(tmp_path))
    import main
    await main.main_async()  # Should succeed with dry-run logic
    # Check at least one output file
    assert any(p.name.startswith("output_s")
               for p in (tmp_path/"outputs").glob("*.md"))
