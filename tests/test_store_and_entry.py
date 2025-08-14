import os, io, runpy, asyncio
import builtins
import types
import pytest

from core.store import FileSystemDocumentStore, InMemoryDocumentStore


def test_filesystem_store_read_write(tmp_path):
    store = FileSystemDocumentStore()
    missing_path = tmp_path/"missing.txt"
    # missing -> empty string
    assert store.read(str(missing_path)) == ""
    assert store.exists(str(missing_path)) is False
    # write then read
    store.write(str(missing_path), "hello")
    assert store.exists(str(missing_path)) is True
    assert store.read(str(missing_path)) == "hello"


def test_inmemory_store(tmp_path):
    mem = InMemoryDocumentStore()
    p = str(tmp_path/"x.md")
    assert mem.read(p) == ""
    assert mem.exists(p) is False
    mem.write(p, "data")
    assert mem.exists(p) is True and mem.read(p) == "data"


@pytest.mark.parametrize("exc_type", [KeyboardInterrupt, RuntimeError])
def test_main_entry_exceptions(monkeypatch, exc_type, tmp_path, capsys, caplog):
    # Patch asyncio.run to raise desired exception
    monkeypatch.setenv("USE_OLLAMA", "true")
    monkeypatch.setenv("DRY_RUN", "true")
    monkeypatch.setenv("NEW_ENGINE", "false")
    # Provide template to avoid word doc errors if reached
    (tmp_path/"template.docx").write_bytes(b"PK\x03\x04fake")

    import config as cfg
    # redirect important dirs
    monkeypatch.setattr(cfg, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(cfg, "DOCS_DIR", str(tmp_path/"docs"))
    monkeypatch.setattr(cfg, "PROCESSED_DOCS_DIR", str(tmp_path/"processed"))
    monkeypatch.setattr(cfg, "OUTPUTS_DIR", str(tmp_path/"outputs"))
    monkeypatch.setattr(cfg, "INSTRUCTIONS_DIR", str(tmp_path/"inst"))
    monkeypatch.setattr(cfg, "LOGS_DIR", str(tmp_path/"logs"))

    os.makedirs(cfg.DOCS_DIR, exist_ok=True)
    os.makedirs(cfg.OUTPUTS_DIR, exist_ok=True)

    # Patch heavy functions so they don't run if exception is after setup
    import utils
    monkeypatch.setattr(utils, "preprocess_all_pdfs", lambda: True)
    monkeypatch.setattr(utils, "merge_output_files", lambda *a, **k: True)
    monkeypatch.setattr(utils, "parse_markdown_to_dict", lambda *a, **k: {})
    monkeypatch.setattr(utils, "generate_word_document", lambda *a, **k: None)
    # Track clear_directory calls
    called = {}
    monkeypatch.setattr(utils, "clear_directory", lambda path: called.setdefault("cleared", path))

    # Fake asyncio.run
    monkeypatch.setattr(asyncio, "run", lambda coro: (_ for _ in ()).throw(exc_type("boom")))

    # Execute main module under __main__ guard
    runpy.run_path("main.py", run_name="__main__")

    captured_out = capsys.readouterr()
    out_text = captured_out.out + captured_out.err
    if exc_type is KeyboardInterrupt:
        assert "Process interrupted by user" in out_text
    else:
        # RuntimeError path: ensure cleanup still executed (graceful handling)
        assert called.get("cleared") == cfg.PROCESSED_DOCS_DIR
    # Ensure cleanup was invoked
    assert "cleared" in called
