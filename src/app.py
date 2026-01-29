from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.load_cedict import load_cedict_lines
from src.parse_cedict import parse_cedict_lines, CedictEntry
from src.build_index import build_char_index

DisplayMode = Literal["both", "simp", "trad"]

CEDICT_PATH = "data/cedict_ts.u8"

# These will be filled at startup
INDEX: dict[str, list[CedictEntry]] = {}
ENTRY_COUNT = 0
CHAR_COUNT = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global INDEX, ENTRY_COUNT, CHAR_COUNT

    lines = load_cedict_lines(CEDICT_PATH)
    entries = parse_cedict_lines(lines)
    INDEX = build_char_index(entries)

    ENTRY_COUNT = len(entries)
    CHAR_COUNT = len(INDEX)

    yield

    INDEX = {}


app = FastAPI(title="ChineseRules API", lifespan=lifespan)

# ✅ CORS — allow your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chineserules.matthewgeier.com",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def entry_to_dict(e: CedictEntry, mode: DisplayMode) -> dict:
    if mode == "simp":
        head = {"word": e.simplified}
    elif mode == "trad":
        head = {"word": e.traditional}
    else:
        head = {"simplified": e.simplified, "traditional": e.traditional}

    return {
        **head,
        "pinyin": e.pinyin,
        "definitions": list(e.definitions),
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "entries": ENTRY_COUNT,
        "unique_characters": CHAR_COUNT,
    }


@app.get("/lookup")
def lookup(
    char: str = Query(..., min_length=1, max_length=1),
    mode: DisplayMode = Query("both"),
    limit: int = Query(25, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    if not INDEX:
        raise HTTPException(status_code=503, detail="Index not loaded yet")

    results = INDEX.get(char, [])
    total = len(results)
    page = results[offset : offset + limit]

    return {
        "query": {"char": char, "mode": mode, "limit": limit, "offset": offset},
        "total": total,
        "results": [entry_to_dict(e, mode) for e in page],
    }


@app.get("/")
def root():
    return {
        "message": "ChineseRules API is running",
        "try": ["/health", "/lookup?char=学"],
    }
