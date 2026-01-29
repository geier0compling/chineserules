from collections import defaultdict
from typing import DefaultDict
from src.parse_cedict import CedictEntry

def build_char_index(entries: list[CedictEntry]) -> dict[str, list[CedictEntry]]:
    index: DefaultDict[str, list[CedictEntry]] = defaultdict(list)

    for entry in entries:
        # index BOTH simplified and traditional chars
        chars = set(entry.simplified) | set(entry.traditional)
        for ch in chars:
            index[ch].append(entry)

    return dict(index)
