from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

from media_extract.udr import new_block_id, now_iso


def extract_image(
    path: Path,
    source_uri: str,
    *,
    ocr: bool = False,
) -> dict[str, Any]:
    raw = path.read_bytes()
    fp = hashlib.sha256(raw).hexdigest()

    warnings: list[str] = []
    ocr_engine = None
    ocr_text = ""
    ocr_confidence: float | None = None

    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)
        w, h = im.size
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        mode = im.mode

    if ocr:
        try:
            import pytesseract

            if shutil.which("tesseract") is None and sys.platform == "win32":
                _win = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
                if _win.is_file():
                    pytesseract.pytesseract.tesseract_cmd = str(_win)

            ocr_engine = "pytesseract"
            with Image.open(path) as im2:
                im2 = ImageOps.exif_transpose(im2)
                if im2.mode not in ("RGB", "L"):
                    im2 = im2.convert("RGB")
                data = pytesseract.image_to_data(im2, lang="chi_sim+eng", output_type=pytesseract.Output.DICT)
            texts = [t for t in data.get("text", []) if (t or "").strip()]
            ocr_text = "\n".join(texts).strip()
            try:
                confs = [int(c) for c in data.get("conf", []) if str(c).lstrip("-").isdigit()]
                if confs:
                    ocr_confidence = max(0.0, min(1.0, sum(confs) / len(confs) / 100.0))
            except Exception:
                ocr_confidence = None
        except ImportError:
            warnings.append("OCR_SKIPPED: pytesseract not installed (pip install pytesseract, optional extra ocr)")
        except Exception as e:
            warnings.append(f"OCR_FAILED: {e!s}")

    document: dict[str, Any] = {
        "sourceFormat": "image",
        "sourceUri": source_uri,
        "fingerprint": fp,
        "originalFilename": path.name,
        "mimeType": _guess_mime(path.suffix),
        "byteSize": len(raw),
        "ingestedAt": now_iso(),
        "pipeline": {
            "libraryVersions": {"Pillow": Image.__version__},
        },
        "image": {
            "widthPx": w,
            "heightPx": h,
            "hasAlpha": bool(has_alpha),
            "exif": {"pilMode": mode},
        },
    }
    if ocr_engine:
        document["pipeline"]["ocrEngine"] = ocr_engine
    if warnings:
        document["pipeline"]["warnings"] = warnings

    blocks: list[dict[str, Any]] = []
    if ocr_text:
        blocks.append(
            {
                "blockId": new_block_id(1),
                "type": "page_ocr",
                "text": ocr_text,
                "confidence": ocr_confidence,
                "location": {"pageIndex": 0},
                "metadata": {"source": "image_ocr"},
            }
        )
    else:
        blocks.append(
            {
                "blockId": new_block_id(1),
                "type": "other",
                "text": f"[Image {w}x{h}px, mode={mode}] 未运行 OCR；使用 --ocr 且安装 Tesseract 可提取图中文字。",
                "confidence": None,
                "location": {"pageIndex": 0},
                "metadata": {
                    "widthPx": w,
                    "heightPx": h,
                    "pilMode": mode,
                },
            }
        )

    return {"schemaVersion": "1.0.0", "document": document, "blocks": blocks, "assets": []}


def _guess_mime(ext: str) -> str:
    ext = ext.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
    }.get(ext, "application/octet-stream")
