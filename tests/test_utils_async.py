import asyncio
import os
import pytest
from utils import read_markdown_file_async, save_markdown_file_async, read_multiple_markdown_files_async


@pytest.mark.asyncio
async def test_async_read_and_cache(tmp_path):
    f = tmp_path / "file.md"
    f.write_text("Hello")
    content1 = await read_markdown_file_async(str(f))
    content2 = await read_markdown_file_async(str(f))  # cached second time
    assert content1 == content2 == "Hello"


@pytest.mark.asyncio
async def test_async_save_and_invalidate(tmp_path):
    f = tmp_path / "file2.md"
    await save_markdown_file_async(str(f), "First")
    c1 = await read_markdown_file_async(str(f))
    assert c1 == "First"
    await save_markdown_file_async(str(f), "Second")
    c2 = await read_markdown_file_async(str(f))
    assert c2 == "Second"


@pytest.mark.asyncio
async def test_read_multiple_markdown_files_async(tmp_path):
    a = tmp_path / "a.md"
    a.write_text("A")
    b = tmp_path / "b.md"
    b.write_text("B")
    combined = await read_multiple_markdown_files_async([str(a), str(b)])
    assert "START OF FILE" in combined and "A" in combined and "B" in combined
