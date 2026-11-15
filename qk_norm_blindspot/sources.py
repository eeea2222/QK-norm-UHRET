"""Source registry and anchor-quote verification against the extracted source texts."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from . import paths

_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
_QUOTES = {ord("‘"): "'", ord("’"): "'", ord("“"): '"', ord("”"): '"', ord(" "): " "}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(_DASHES).translate(_QUOTES)
    return re.sub(r"\s+", " ", text).strip()


def _dehyphen(text: str) -> str:
    # 'detec- tor' -> 'detector' after whitespace normalisation
    return re.sub(r"(\w)- (\w)", r"\1\2", text)


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


@lru_cache(maxsize=256)
def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def text_path(doc_id: str) -> Path:
    return paths.TEXT_DIR / f"{doc_id}.txt"


def page_text(doc_id: str, pdf_page: int | None, text_file: str | None = None) -> str | None:
    """Text of a 1-based PDF page (pages separated by form feeds) or the whole document."""
    p = Path(text_file) if text_file else text_path(doc_id)
    if not p.is_absolute():
        p = paths.ROOT / p
    if not p.exists():
        return None
    txt = _read_text(str(p))
    if pdf_page is None:
        return txt
    pages = txt.split("\f")
    if 1 <= pdf_page <= len(pages):
        return pages[pdf_page - 1]
    return None


def anchor_found(anchor: str, haystack: str | None) -> bool:
    if not anchor or haystack is None:
        return False
    a, h = normalize(anchor), normalize(haystack)
    if a in h:
        return True
    return _dehyphen(a) in _dehyphen(h)


def verify_anchor(doc_id: str, pdf_page: int | None, anchor: str, text_file: str | None = None) -> dict:
    """Return {'found': bool, 'checked_in': ..., 'page_found': int|None}.

    Looks on the cited page first; if not there, searches the whole document so a wrong page
    number is reported (found_on_other_page) instead of silently passing.
    """
    page = page_text(doc_id, pdf_page, text_file)
    if anchor_found(anchor, page):
        return {"found": True, "page_found": pdf_page, "checked_in": text_file or str(paths.rel(text_path(doc_id)))}
    whole = page_text(doc_id, None, text_file)
    if whole is not None and pdf_page is not None:
        for i, pg in enumerate(whole.split("\f"), start=1):
            if anchor_found(anchor, pg):
                return {"found": False, "found_on_other_page": i, "page_found": i,
                        "checked_in": text_file or str(paths.rel(text_path(doc_id)))}
    return {"found": False, "page_found": None, "checked_in": text_file or str(paths.rel(text_path(doc_id)))}


def load_registry() -> dict[str, dict]:
    """doc_id -> document metadata, from sources/raw/*/meta.json plus curated documents."""
    reg: dict[str, dict] = {}
    for meta in sorted(paths.RAW_DIR.glob("*/meta.json")):
        try:
            m = json.loads(meta.read_text())
        except json.JSONDecodeError:
            continue
        doc_id = m.get("doc_id") or meta.parent.name
        m.setdefault("doc_id", doc_id)
        m["meta_path"] = paths.rel(meta)
        reg[doc_id] = m
    curated = paths.CURATION_DIR / "documents.json"
    if curated.exists():
        for d in json.loads(curated.read_text())["documents"]:
            reg.setdefault(d["doc_id"], {}).update(d)
    return reg
