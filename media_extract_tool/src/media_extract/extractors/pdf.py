from __future__ import annotations

import hashlib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import fitz

from media_extract.udr import new_block_id, now_iso


def _pymupdf_version() -> str:
    try:
        return version("PyMuPDF")
    except PackageNotFoundError:
        return "unknown"


def _flatten_toc_simple(toc: list) -> list[dict[str, Any]]:
    """get_toc(simple=True) -> [lvl, title, page]"""
    out: list[dict[str, Any]] = []
    for row in toc:
        if not row or len(row) < 3:
            continue
        _lvl, title, page = row[0], row[1], row[2]
        out.append({"title": str(title).strip(), "pageIndex": max(0, int(page) - 1)})
    return out


def extract_pdf(path: Path, source_uri: str, *, password: str | None = None) -> dict[str, Any]:
    raw = path.read_bytes()
    fp = hashlib.sha256(raw).hexdigest()

    doc = fitz.open(str(path))
    try:
        is_encrypted = bool(getattr(doc, "is_encrypted", False) or doc.needs_pass)
        if doc.needs_pass:
            if not password:
                raise ValueError("PDF_PASSWORD_REQUIRED")
            if not doc.authenticate(password):
                raise ValueError("PDF_PASSWORD_INVALID")

        page_count = doc.page_count
        outline_raw = doc.get_toc(simple=True)
        outline = _flatten_toc_simple(outline_raw)
        blocks: list[dict[str, Any]] = []
        n = 0
        text_chars = 0
        for pi in range(page_count):
            page = doc.load_page(pi)
            txt = page.get_text("text") or ""
            text_chars += len(txt.strip())
            if txt.strip():
                n += 1
                blocks.append(
                    {
                        "blockId": new_block_id(n),
                        "type": "paragraph",
                        "text": txt.strip(),
                        "confidence": None,
                        "location": {"pageIndex": pi},
                    }
                )
        is_likely_scanned = page_count > 0 and text_chars < max(20, page_count * 5)

        document: dict[str, Any] = {
            "sourceFormat": "pdf",
            "sourceUri": source_uri,
            "fingerprint": fp,
            "originalFilename": path.name,
            "mimeType": "application/pdf",
            "byteSize": len(raw),
            "ingestedAt": now_iso(),
            "pipeline": {
                "libraryVersions": {"PyMuPDF": _pymupdf_version()},
            },
            "pdf": {
                "pageCount": page_count,
                "isEncrypted": is_encrypted,
                "isLikelyScanned": is_likely_scanned,
            },
        }
        if outline:
            document["pdf"]["outline"] = outline

        return {"schemaVersion": "1.0.0", "document": document, "blocks": blocks, "assets": []}
    finally:
        doc.close()
