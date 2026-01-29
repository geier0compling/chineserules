from pathlib import Path


def load_cedict_lines(path: str | Path) -> list[str]:
    """
    Loads the raw CC-CEDICT file and returns a list of non-comment, non-empty lines.
    """
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"CEDICT file not found at: {p.resolve()}")

    lines: list[str] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            lines.append(line)

    return lines
