import os
import importlib
import pytest


@pytest.fixture(autouse=True)
def _ollama_env(monkeypatch):
    # Ensure config loads in local mode and no network chat occurs in creation tests
    monkeypatch.setenv("USE_OLLAMA", "true")
    monkeypatch.setenv("DRY_RUN", "true")


def _reload_config():
    import config
    import importlib
    importlib.reload(config)
    return config


def test_preprocess_all_pdfs_success(monkeypatch, tmp_path):
    config = _reload_config()
    # Redirect dirs
    monkeypatch.setattr(config, "DOCS_DIR", str(tmp_path/"docs"))
    monkeypatch.setattr(config, "PROCESSED_DOCS_DIR",
                        str(tmp_path/"processed"))
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    # Create fake pdf file
    pdf_path = os.path.join(config.DOCS_DIR, "sample.pdf")
    open(pdf_path, "wb").write(b"%PDF-1.4\n%EOF")

    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        def __init__(self, path):
            self.pages = [FakePage("Hello World"), FakePage(
                "Second Page")]  # two pages

    import pypdf
    monkeypatch.setattr(pypdf, "PdfReader", FakeReader)
    import utils
    ok = utils.preprocess_all_pdfs()
    assert ok is True
    # Output file created with .txt appended
    out_files = list((tmp_path/"processed").glob("*.pdf.txt"))
    assert len(out_files) == 1
    content = out_files[0].read_text()
    assert "Hello World" in content and "Second Page" in content


def test_preprocess_all_pdfs_blank_pages(monkeypatch, tmp_path):
    config = _reload_config()
    monkeypatch.setattr(config, "DOCS_DIR", str(tmp_path/"docs2"))
    monkeypatch.setattr(config, "PROCESSED_DOCS_DIR",
                        str(tmp_path/"processed2"))
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    open(os.path.join(config.DOCS_DIR, "empty.pdf"),
         "wb").write(b"%PDF-1.4\n%EOF")

    class BlankPage:
        def extract_text(self):
            return ""  # no text

    class BlankReader:
        def __init__(self, path):
            self.pages = [BlankPage()]

    import pypdf
    monkeypatch.setattr(pypdf, "PdfReader", BlankReader)
    import utils
    ok = utils.preprocess_all_pdfs()
    assert ok is True  # still returns True
    # No output file because no text extracted
    assert list((tmp_path/"processed2").glob("*.txt")) == []


def test_preprocess_all_pdfs_exception(monkeypatch, tmp_path):
    config = _reload_config()
    monkeypatch.setattr(config, "DOCS_DIR", str(tmp_path/"docs3"))
    monkeypatch.setattr(config, "PROCESSED_DOCS_DIR",
                        str(tmp_path/"processed3"))
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    open(os.path.join(config.DOCS_DIR, "boom.pdf"), "wb").write(b"%PDF-1.4\n%EOF")

    def raising_reader(path):
        raise RuntimeError("read fail")

    import pypdf
    monkeypatch.setattr(pypdf, "PdfReader", raising_reader)
    import utils
    ok = utils.preprocess_all_pdfs()
    assert ok is False


def test_create_writer_team_registration(monkeypatch):
    _reload_config()
    import writer
    # Capture register_function calls
    calls = []
    import autogen

    def fake_register(func, caller, executor, name, description):
        calls.append(name)
    monkeypatch.setattr(autogen.agentchat, "register_function", fake_register)
    mgr = writer.create_writer_team({"config_list": [{"model": "m", "api_key": "k", "base_url": "http://l", "api_type": "openai"}]},
                                    {"config_list": [{"model": "fast", "api_key": "k", "base_url": "http://l", "api_type": "openai"}]})
    agent_names = {a.name for a in mgr.groupchat.agents}
    assert {"Writer_User_Proxy", "Document_Writer",
            "Planner"}.issubset(agent_names)
    assert set(calls) == {"read_markdown_file_async", "list_files_in_directory",
                          "save_markdown_file_async", "read_multiple_markdown_files_async"}


def test_create_validator_team_registration(monkeypatch):
    _reload_config()
    import validator
    import autogen
    calls = []

    def fake_register(func, caller, executor, name, description):
        calls.append(name)
    monkeypatch.setattr(autogen.agentchat, "register_function", fake_register)
    mgr = validator.create_validator_team({"config_list": [{"model": "m", "api_key": "k", "base_url": "http://l", "api_type": "openai"}]},
                                          {"config_list": [{"model": "fast", "api_key": "k", "base_url": "http://l", "api_type": "openai"}]})
    agent_names = {a.name for a in mgr.groupchat.agents}
    assert {"Validator_User_Proxy", "Quality_Assessor",
            "Fact_Checker"}.issubset(agent_names)
    assert set(calls) == {"read_markdown_file_async", "list_files_in_directory",
                          "save_markdown_file_async", "read_multiple_markdown_files_async"}
