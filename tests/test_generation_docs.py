from generation_docs import generation_docs


def test_a1_keeps_only_a1_level_section():
    docs = generation_docs("A1")
    assert "### A1\n" in docs
    assert "### A2\n" not in docs
    assert "### C1–C2" not in docs


def test_c2_keeps_c2_and_shared_c1_c2_sections():
    docs = generation_docs("C2")
    assert "### C2\n" in docs
    assert "### C1–C2" in docs
    assert "### C1\n" not in docs
    assert "### B2\n" not in docs


def test_shared_guide_sections_are_kept_for_every_level():
    for level in ("A1", "C2"):
        docs = generation_docs(level)
        assert "## Rules" in docs
        assert "**Banned situations:**" in docs


def test_formats_are_filtered_by_level():
    a1 = generation_docs("A1")
    assert "| Word bank | A1–B1 |" in a1
    assert "Choose the nuance |" not in a1
    c1 = generation_docs("C1")
    assert "| Choose the nuance | C1–C2 |" in c1
    assert "| Word bank |" not in c1


def test_formats_table_header_is_kept():
    assert "| Format | Levels |" in generation_docs("B1")
