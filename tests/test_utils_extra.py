import os
import pytest
import utils
from pathlib import Path


def test_is_terminate_message_variants():
    assert utils.is_terminate_message({"content": "Done TERMINATE"}) is True
    assert utils.is_terminate_message({"content": "Done"}) is False
    assert utils.is_terminate_message({"no": "key"}) is False
    assert utils.is_terminate_message(
        "TERMINATE") is False  # only dicts accepted


def test_clean_text_private():
    fn = getattr(utils, "_clean_text")
    raw = "Line1\n\n\nLine2   \n   Line3"
    out = fn(raw)
    assert "\n\n" in out and out.startswith("Line1") and out.endswith("Line3")


def test_clear_directory(tmp_path):
    d = tmp_path/"d"
    d.mkdir()
    (d/"file.txt").write_text("x")
    sub = d/"sub"
    sub.mkdir()
    (sub/"inner.txt").write_text("y")
    utils.clear_directory(str(d))
    assert list(d.iterdir()) == []


def test_merge_output_files_io_error(monkeypatch, tmp_path):
    monkeypatch.setattr("builtins.open", lambda *a, **
                        k: (_ for _ in ()).throw(IOError("disk full")))
    ok = utils.merge_output_files(1, str(tmp_path), "final.md")
    assert ok is False


def test_parse_feedback_error_path(monkeypatch):
    import re as real_re

    def boom(*a, **k):
        raise RuntimeError("regex fail")
    monkeypatch.setattr(real_re, "search", boom)
    counts = utils.parse_feedback_and_count_issues(
        "[FEEDBACK_SUMMARY][END_FEEDBACK_SUMMARY]")
    assert counts == {"critical": 0, "major": 0, "minor": 0}


def test_generate_word_document(monkeypatch, tmp_path):
    tpl = tmp_path/"template.docx"
    tpl.write_bytes(b"PK\x03\x04fake")
    out = tmp_path/"out.docx"

    class FakeDoc:
        def __init__(self, path):
            self.path = path
            self.rendered = False

        def render(self, context):
            self.rendered = True

        def save(self, path):
            with open(path, 'wb') as f:
                f.write(b'OK')
    import utils as u2
    monkeypatch.setattr(u2, "DocxTemplate", FakeDoc)
    utils.generate_word_document({"a": 1}, str(tpl), str(out))
    assert out.exists()


@pytest.mark.asyncio
async def test_read_multiple_markdown_files_async_error(monkeypatch, tmp_path):
    import utils as u3
    original = u3._read_and_cache_multiple_files_sync

    def explode(filepaths_tuple):
        raise ValueError("boom")
    monkeypatch.setattr(u3, "_read_and_cache_multiple_files_sync", explode)
    with pytest.raises(ValueError):
        await u3.read_multiple_markdown_files_async([str(tmp_path/"a.md")])
    monkeypatch.setattr(u3, "_read_and_cache_multiple_files_sync", original)
