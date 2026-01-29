from src.load_cedict import load_cedict_lines
from src.parse_cedict import parse_cedict_lines, CedictEntry
from src.build_index import build_char_index, sort_index


def format_entry(e: CedictEntry, mode: str) -> str:
    """
    mode:
      - "both": show simplified + traditional
      - "simp": show simplified only
      - "trad": show traditional only
    """
    defs = "; ".join(e.definitions[:2])  # keep output readable

    if mode == "simp":
        head = f"{e.simplified} [{e.pinyin}]"
    elif mode == "trad":
        head = f"{e.traditional} [{e.pinyin}]"
    else:
        head = f"{e.simplified} ({e.traditional}) [{e.pinyin}]"

    return f"{head} — {defs}"


def main() -> None:
    cedict_path = "data/cedict_ts.u8"

    lines = load_cedict_lines(cedict_path)
    print(f"Loaded {len(lines):,} non-comment lines")

    entries = parse_cedict_lines(lines)
    print(f"Parsed {len(entries):,} entries")

    index = build_char_index(entries)
    sort_index(index)
    print(f"Index has {len(index):,} unique characters\n")

    # NEW: display mode
    mode = "both"
    print("Display mode: both | simp | trad")
    print("Commands: /mode both   /mode simp   /mode trad\n")

    while True:
        q = input("Type 1 Chinese character (or 'quit'): ").strip()

        if q.lower() in ("quit", "q", "exit"):
            break

        # NEW: mode command
        if q.startswith("/mode"):
            parts = q.split()
            if len(parts) == 2 and parts[1] in ("both", "simp", "trad"):
                mode = parts[1]
                print(f"✅ Display mode set to: {mode}\n")
            else:
                print("Usage: /mode both | /mode simp | /mode trad\n")
            continue

        if len(q) != 1:
            print("Please type exactly ONE character.\n")
            continue

        results = index.get(q, [])
        print(f"Found {len(results):,} words containing '{q}' (display: {mode})")
        for e in results[:25]:
            print(" - " + format_entry(e, mode))
        if len(results) > 25:
            print(f"... ({len(results) - 25:,} more)")
        print()


if __name__ == "__main__":
    main()
