from __future__ import annotations

from pathlib import Path


def default_udr_schema_path() -> Path:
    """与 `media_extract` 包同目录下的 `schemas/`。"""
    pkg = Path(__file__).resolve().parent
    return pkg / "schemas" / "unified-document-representation.schema.json"
