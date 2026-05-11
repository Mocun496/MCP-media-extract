from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

from media_extract.schema_path import default_udr_schema_path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


_blk = re.compile(r"^blk_[a-zA-Z0-9_-]+$")


def new_block_id(n: int) -> str:
    s = f"blk_{n:06d}"
    if not _blk.match(s):
        raise ValueError(s)
    return s


def validate_udr(data: dict[str, Any], schema_path: Path | None = None) -> None:
    path = schema_path or default_udr_schema_path()
    if not path.is_file():
        raise FileNotFoundError(f"UDR schema not found: {path}")
    with path.open(encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=data, schema=schema)


def udr_text_concat(blocks: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for b in blocks:
        t = (b.get("text") or "").strip()
        if t:
            parts.append(t)
    return "\n\n".join(parts)
