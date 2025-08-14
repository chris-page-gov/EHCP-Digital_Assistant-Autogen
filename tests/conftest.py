import config as app_config
import os
import tempfile
import shutil
import pytest

# Force local (Ollama) mode for test imports so missing Azure env vars don't break import
os.environ.setdefault("USE_OLLAMA", "true")


@pytest.fixture(autouse=True)
def ensure_output_dirs(tmp_path, monkeypatch):
    # Ensure required directories exist for tests that may touch filesystem
    for d in [app_config.OUTPUTS_DIR, app_config.PROCESSED_DOCS_DIR, app_config.DOCS_DIR]:
        os.makedirs(d, exist_ok=True)
    yield


@pytest.fixture
def sample_feedback_block():
    return (
        "Some intro text\n[FEEDBACK_SUMMARY]\nCritical: 2\nMajor: 5\nMinor: 7\n[END_FEEDBACK_SUMMARY]\nTail text"
    )
