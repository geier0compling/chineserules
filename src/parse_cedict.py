import re
from dataclasses import dataclass


# Example line:
# 傳統 简体 [pin1 yin1] /def1/def2/
_CEDICT_RE = re.compile(r"^(?P<trad>\S+)\s+(?P<simp>\S+)\s+\[(?P<pinyin>.+?)\]\s+/(?P<defs>.+)/$")


@dataclass(frozen=True)
class CedictEntry:
    traditional: str
    simplified: str
    pinyin: str
    definitions: tuple[str, ...]


def parse_cedict_line(line: str) -> CedictEntry | None:
    """
    Parse a single CEDICT line into a CedictEntry.
    Returns None if the line doesn't match the expected format.
    """
    m = _CEDICT_RE.match(line)
    if not m:
        return None

    trad = m.group("trad")
    simp = m.group("simp")
    pinyin = m.group("pinyin").strip()

    # defs are slash-separated; remove empties
    defs_raw = m.group("defs")
    defs_list = [d.strip() for d in defs_raw.split("/") if d.strip()]

    return CedictEntry(
        traditional=trad,
        simplified=simp,
        pinyin=pinyin,
        definitions=tuple(defs_list),
    )


def parse_cedict_lines(lines: list[str]) -> list[CedictEntry]:
    """
    Parse all lines; silently skips malformed lines.
    """
    entries: list[CedictEntry] = []
    skipped = 0

    for line in lines:
        entry = parse_cedict_line(line)
        if entry is None:
            skipped += 1
            continue
        entries.append(entry)

    # Optional: you can print skipped count in main.py if you want
    return entries
