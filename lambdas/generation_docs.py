from pathlib import Path

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

GUIDE = (Path(__file__).parent / "cefr_level_guide.md").read_text(encoding="utf-8")
FORMATS = (Path(__file__).parent / "exercise_formats.md").read_text(encoding="utf-8")


def _covers(levels_text, level):
    # levels_text is one level ("B1") or a range ("A2–C2")
    first, _, last = levels_text.strip().partition("–")
    return LEVELS.index(first) <= LEVELS.index(level) <= LEVELS.index(last or first)


def _guide_for(level):
    # Keeps a "### <levels>" section only if it covers the level
    lines, keep = [], True
    for line in GUIDE.splitlines():
        if line.startswith("### "):
            keep = _covers(line[4:], level)
        elif line.startswith("#"):
            keep = True
        if keep:
            lines.append(line)
    return "\n".join(lines)


def _formats_for(level):
    # Keeps a table row only if its Levels column covers the level
    lines = []
    for line in FORMATS.splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if line.startswith("|") and cells[1][:2] in LEVELS and not _covers(cells[1], level):
            continue
        lines.append(line)
    return "\n".join(lines)


def generation_docs(level):
    """System prompt part with the guide and formats for one learner level."""
    return f"""

Follow this guide when writing the exercises:
<guide>
{_guide_for(level)}
</guide>

Use only these exercise formats:
<formats>
{_formats_for(level)}
</formats>

Do the planning from the guide in your head. Do not write the plan, notes or drafts: your whole reply is the final JSON object and nothing else.

In expected_answer write only the correct answer and, if there are any, the accepted alternatives separated by " / ". No explanations, rule names or reasons, except the five-word reason the "Choose the nuance" format asks for."""
