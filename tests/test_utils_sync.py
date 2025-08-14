import os
import re
import tempfile
from utils import parse_feedback_and_count_issues, list_files_in_directory, merge_output_files, parse_markdown_to_dict, _sanitise_key
import config


def test_parse_feedback_and_count_issues(sample_feedback_block):
    counts = parse_feedback_and_count_issues(sample_feedback_block)
    assert counts == {"critical": 2, "major": 5, "minor": 7}


def test_parse_feedback_missing_block():
    counts = parse_feedback_and_count_issues("No block here")
    assert counts == {"critical": 0, "major": 0, "minor": 0}


def test_list_files_in_directory(tmp_path):
    f1 = tmp_path / "a.txt"
    f1.write_text("hi")
    f2 = tmp_path / "b.md"
    f2.write_text("yo")
    files = list_files_in_directory(str(tmp_path))
    assert len(files) == 2
    assert any(str(f1) == p for p in files)


def test_merge_output_files(tmp_path):
    # create pseudo output files
    for i in range(1, 4):
        (tmp_path / f"output_s{i}.md").write_text(f"Section {i}")
    ok = merge_output_files(3, str(tmp_path), "final_document.md")
    assert ok is True
    merged = (tmp_path / "final_document.md").read_text()
    assert "Section 1" in merged and "Section 3" in merged


def test_merge_output_files_missing(tmp_path, caplog):
    (tmp_path / "output_s1.md").write_text("Only one")
    ok = merge_output_files(2, str(tmp_path), "final.md")
    assert ok is False


def test_parse_markdown_to_dict(tmp_path):
    md = tmp_path / "sample.md"
    md.write_text(
        """**Name:** John Smith\nRandom line\n**History Summary:** Some history here.\n---\n**Another Key:** Value\n""")
    d = parse_markdown_to_dict(str(md))
    name_val = d.get("name", "")
    hist_val = d.get("history_summary", "")
    assert name_val.startswith("John Smith")
    assert "Random line" in name_val
    assert hist_val.startswith("Some history")


def test_sanitise_key_variations():
    assert _sanitise_key("Child's Needs") == "child_needs"
    assert _sanitise_key(
        "Comms & Interaction - Need 1") == "comms_interaction_need_1"
